import base64
import functools
import io
import json
import os
import secrets
import sqlite3
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, session, render_template, send_file
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from course_xml import *

DEFAULTS = dict(level='beginner', language='en', currency='USD', price=0, durationHours=0, isPublished=False, isFeatured=False, isFree=False, certificationIncluded=True)

def create_app(database=None):
    app = Flask(__name__)
    Path(app.instance_path).mkdir(exist_ok=True)
    keypath = Path(app.instance_path)/'session.key'
    if not keypath.exists():
        fd = os.open(keypath, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        with os.fdopen(fd,'w') as f: f.write(secrets.token_hex(32))
    app.config.update(SECRET_KEY=keypath.read_text(), MAX_CONTENT_LENGTH=MAX_PACKAGE, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Strict', DATABASE=database or str(Path(app.instance_path)/'courses.sqlite'))
    def connect():
        db = sqlite3.connect(app.config['DATABASE']); db.row_factory = sqlite3.Row
        return db
    with connect() as db:
        db.executescript('CREATE TABLE IF NOT EXISTS courses (id TEXT PRIMARY KEY, data TEXT NOT NULL); CREATE TABLE IF NOT EXISTS admins (email TEXT PRIMARY KEY, password TEXT NOT NULL);')
    def admin(fn):
        @functools.wraps(fn)
        def wrapped(*args,**kwargs):
            if not session.get('admin'): return jsonify(error='Sign in as an administrator'),401
            if request.method not in ('GET','HEAD') and not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','')):
                return jsonify(error='Invalid security token. Reload and retry.'),403
            return fn(*args,**kwargs)
        return wrapped
    def all_courses(db): return [dict(id=r['id'],**json.loads(r['data'])) for r in db.execute('SELECT * FROM courses')]
    def find(db, cid):
        row=db.execute('SELECT * FROM courses WHERE id=?',(cid,)).fetchone()
        if not row: raise LookupError('Course not found')
        return json.loads(row['data'])
    def save(db,cid,pkg): db.execute('INSERT OR REPLACE INTO courses VALUES (?,?)',(cid,json.dumps(pkg)))
    def normalize(pkg):
        pkg.pop('id',None)
        c=pkg['course']
        if not isinstance(c.get('title'),str) or not c['title'].strip(): raise ValueError('Course title is required')
        c['title']=c['title'].strip()
        for key in NUM:
            if c.get(key) is not None: c[key]=number(c[key])
        for key in BOOL:
            if key in c: c[key]=boolean(c[key])
        for key in LISTS:
            if not isinstance(c.get(key,[]),list) or any(not isinstance(x,str) for x in c.get(key,[])): raise ValueError(key+' must be a list of text')
        for lesson in pkg['lessons']:
            if not lesson.get('title','').strip(): raise ValueError('Lesson title is required')
            lesson.setdefault('id',str(uuid.uuid4())); lesson['slug']=lesson.get('slug') or slugify(lesson['title'])
            lesson.setdefault('isPublished',True)
            for key in LNUM: lesson[key]=number(lesson.get(key,0))
            for key in LTEXT: lesson.setdefault(key,'')
            lesson.setdefault('lab',{}); lesson.setdefault('quiz',[]); lesson.setdefault('resources',[])
            if not isinstance(lesson['lab'],dict) or not isinstance(lesson['quiz'],list) or not isinstance(lesson['resources'],list): raise ValueError('Invalid lesson activities')
            for question in lesson['quiz']:
                if not isinstance(question,dict) or not isinstance(question.get('options',[]),list): raise ValueError('Invalid quiz question')
                for option in question.get('options',[]):
                    if not isinstance(option,dict) or not isinstance(option.get('text',''),str): raise ValueError('Invalid quiz option')
                    option['correct']=boolean(option.get('correct',False))
            for resource in lesson['resources']:
                if resource.get('file'):
                    raw=base64.b64decode(resource['file']['data'],validate=True)
                    if len(raw)>=MAX_FILE: raise ValueError('Embedded file must be smaller than 32 MB')
                    resource['fileSize']=len(raw)
        c['lessons']=len(pkg['lessons']); c['durationHours']=round(sum(l['durationMinutes'] for l in pkg['lessons'])/60,2)
        c['quizCount']=sum(bool(l['quiz']) for l in pkg['lessons']); c['labCount']=sum(bool(l['lab'].get('instructions')) for l in pkg['lessons'])
        return pkg
    @app.errorhandler(Exception)
    def errors(exc):
        if isinstance(exc,HTTPException): return jsonify(error=exc.description),exc.code
        if isinstance(exc,LookupError): return jsonify(error=str(exc)),404
        if isinstance(exc,(ValueError,KeyError,TypeError,ET.ParseError)) or exc.__class__.__module__.startswith('defusedxml'):
            return jsonify(error=str(exc)),400
        app.logger.exception('Request failed'); return jsonify(error='An internal error occurred'),500
    @app.get('/')
    def index(): return render_template('index.html')
    @app.get('/api/session')
    def state():
        with connect() as db: setup=db.execute('SELECT count(*) FROM admins').fetchone()[0]==0
        session.setdefault('csrf',secrets.token_hex(32))
        return jsonify(authenticated=bool(session.get('admin')),setupRequired=setup,csrf=session['csrf'])
    @app.post('/api/auth/<action>')
    def auth(action):
        if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','')): return jsonify(error='Reload the page and retry'),403
        data=request.get_json(); email=data.get('email','').strip().lower(); password=data.get('password','')
        with connect() as db:
            if action=='setup':
                db.execute('BEGIN IMMEDIATE')
                if db.execute('SELECT count(*) FROM admins').fetchone()[0]: return jsonify(error='Administrator already configured'),409
                if '@' not in email or len(password)<12: raise ValueError('Use a valid email and a password of at least 12 characters')
                db.execute('INSERT INTO admins VALUES (?,?)',(email,generate_password_hash(password)))
            elif action=='login':
                row=db.execute('SELECT password FROM admins WHERE email=?',(email,)).fetchone()
                if not row or not check_password_hash(row[0],password): return jsonify(error='Invalid email or password'),401
            else: raise ValueError('Unknown action')
        session.clear(); session['admin']=email; session['csrf']=secrets.token_hex(32)
        return jsonify(csrf=session['csrf'])
    @app.post('/api/logout')
    @admin
    def logout(): session.clear(); return jsonify(ok=True)
    @app.get('/api/courses')
    @admin
    def listing():
        with connect() as db: return jsonify(all_courses(db))
    @app.post('/api/courses')
    @admin
    def create():
        pkg=request.get_json(); pkg['course']={**DEFAULTS,**pkg['course']}; normalize(pkg)
        with connect() as db:
            courses=all_courses(db); slug=slugify(pkg['course'].get('slug') or pkg['course']['title']); unique=slug; suffix=2
            while any(x['course']['slug']==unique for x in courses): unique=f'{slug}-{suffix}'; suffix+=1
            pkg['course']['slug']=unique; cid=str(uuid.uuid4()); save(db,cid,pkg)
        return jsonify(id=cid,**pkg),201
    @app.put('/api/courses/<cid>')
    @admin
    def update(cid):
        pkg=normalize(request.get_json())
        with connect() as db:
            existing=find(db,cid); pkg['course']['slug']=existing['course']['slug']; save(db,cid,pkg)
        return jsonify(id=cid,**pkg)
    @app.delete('/api/courses/<cid>')
    @admin
    def delete(cid):
        with connect() as db: find(db,cid); db.execute('DELETE FROM courses WHERE id=?',(cid,))
        return jsonify(ok=True)
    @app.get('/api/admin/course-packages/export')
    @admin
    def export():
        cid=request.args.get('courseId'); name=request.args.get('name','').strip().casefold()
        if not cid and not name: raise ValueError('Provide courseId or full course name')
        with connect() as db:
            if cid: pkg=find(db,cid)
            else:
                match=next((x for x in all_courses(db) if name in (x['course']['title'].casefold(),x['course']['slug'].casefold())),None)
                if not match: raise LookupError('No course with that name exists to export')
                pkg=match
        filename=re.sub(r'[^a-zA-Z0-9_-]','_',pkg['course']['slug'])[:80]+'.course.xml'
        response=send_file(io.BytesIO(serialize_package(pkg)),mimetype='application/xml',as_attachment=True,download_name=filename)
        from urllib.parse import quote
        response.headers['X-Course-Title']=quote(pkg['course']['title'])
        return response
    @app.post('/api/admin/course-packages/import')
    @admin
    def import_course():
        upload=request.files.get('file')
        if not upload: raise ValueError('Choose an XML file')
        pkg=parse_package(upload.read()); c=pkg['course']; incoming=pkg['lessons']
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing=all_courses(db)
            match=next((x for x in existing if c.get('slug') and x['course']['slug']==c['slug']),None)
            match=match or next((x for x in existing if x['course']['title'].strip().casefold()==c['title'].strip().casefold()),None)
            cid=match['id'] if match else str(uuid.uuid4()); old=match['lessons'] if match else []
            if match:
                merged=dict(match['course'])
                for k,v in c.items():
                    if k=='slug': continue
                    if k in TEXT and k!='title' and not v: continue
                    if k=='instructor': continue
                    merged[k]=v
                c=merged
            else:
                c={**DEFAULTS,**c}; c.pop('instructor',None)
                slug=slugify(c.get('slug') or c['title']); c['slug']=slug; suffix=2
                while any(x['course']['slug']==c['slug'] for x in existing): c['slug']=f'{slug}-{suffix}'; suffix+=1
            # Instructors refer only to existing administrator profiles, never create accounts.
            ins=pkg['course'].get('instructor',{})
            if ins.get('email') and db.execute('SELECT 1 FROM admins WHERE email=?',(ins['email'].lower(),)).fetchone(): c['instructor']=ins
            seen=set(); lessons=list(old); created=updated=0
            for lesson in incoming:
                found=next((l for l in lessons if lesson.get('slug') and l['slug']==lesson['slug']),None)
                found=found or next((l for l in lessons if l['title'].strip().casefold()==lesson['title'].strip().casefold()),None)
                lesson['id']=found['id'] if found else str(uuid.uuid4()); seen.add(lesson['id'])
                if found: lessons[lessons.index(found)]=lesson; updated+=1
                else: lessons.append(lesson); created+=1
            removed=0
            if request.form.get('replace')=='true' and incoming:
                removed=sum(l['id'] not in seen for l in lessons); lessons=[l for l in lessons if l['id'] in seen]
            result=normalize({'course':c,'lessons':lessons}); save(db,cid,result)
        return jsonify(created=not bool(match),courseId=cid,courseTitle=c['title'],courseSlug=c['slug'],lessons=len(incoming),lessonsCreated=created,lessonsUpdated=updated,files=sum(bool(r.get('file')) for l in incoming for r in l.get('resources',[])),removedLessons=removed)
    @app.get('/api/courses/<cid>/lessons/<lid>/resources/<int:index>')
    @admin
    def download(cid,lid,index):
        with connect() as db: pkg=find(db,cid)
        lesson=next((l for l in pkg['lessons'] if l['id']==lid),None)
        if not lesson or index>=len(lesson['resources']): raise LookupError('Resource not found')
        r=lesson['resources'][index]
        if not r.get('file'): raise LookupError('Resource has no embedded file')
        return send_file(io.BytesIO(base64.b64decode(r['file']['data'])),mimetype='application/octet-stream',as_attachment=True,download_name=r.get('fileName','resource'))
    return app

if __name__=='__main__': create_app().run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
