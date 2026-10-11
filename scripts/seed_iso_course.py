"""Seed the XML course locally without credentials or overwriting edited courses."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sqlite3
import sys
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from course_xml import parse_package,serialize_package
ROOT=Path(__file__).resolve().parents[1]

def seed(database):
    pkg=parse_package((ROOT/'seeds/iso27001-introduction.course.xml').read_bytes())
    lessons=pkg['lessons']; assert len(lessons)==10
    for lesson in lessons:
        assert lesson['lab']['instructions'] and len(lesson['quiz'])==3 and lesson['resources']
        assert all(sum(bool(o['correct']) for o in q['options'])==1 for q in lesson['quiz'])
        lesson['id']=str(uuid.uuid5(uuid.NAMESPACE_URL,pkg['course']['slug']+'/'+lesson['slug']))
    c=pkg['course'];c.update(lessons=len(lessons),durationHours=round(sum(l['durationMinutes'] for l in lessons)/60,2),quizCount=sum(bool(l['quiz']) for l in lessons),labCount=sum(bool(l['lab']['instructions']) for l in lessons))
    # Check portability before any database write.
    roundtrip=parse_package(serialize_package(pkg));assert len(roundtrip['lessons'])==10
    database=Path(database)
    if not database.exists(): raise RuntimeError('Initialize the application database before seeding')
    with sqlite3.connect(database) as db:
        backups=database.parent/'backups';backups.mkdir(exist_ok=True)
        backup=backups/('before-iso-seed-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.sqlite')
        with sqlite3.connect(backup) as dest:db.backup(dest)
        db.execute('BEGIN IMMEDIATE')
        for cid,data in db.execute('SELECT id,data FROM courses'):
            existing=json.loads(data)['course']
            if existing.get('slug')==c['slug'] or existing.get('title','').casefold()==c['title'].casefold():
                print('Already seeded; preserving existing course:',cid)
                return cid
        cid=str(uuid.uuid5(uuid.NAMESPACE_URL,'cyberacademy-course/'+c['slug']))
        db.execute('INSERT INTO courses(id,data) VALUES (?,?)',(cid,json.dumps(pkg,ensure_ascii=False)))
    print(json.dumps({'courseId':cid,'title':c['title'],'lessons':10,'quizQuestions':30,'labs':10,'embeddedWorksheets':10,'resources':sum(len(l['resources']) for l in lessons),'durationHours':c['durationHours'],'backup':str(backup)},indent=2))
    return cid
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--database',default=str(ROOT/'instance/courses.sqlite'))
    seed(parser.parse_args().database)
