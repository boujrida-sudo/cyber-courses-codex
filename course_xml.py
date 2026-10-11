"""CyberAcademy 1.0 XML mapping. No DTDs, entities, or external fetches."""
import base64
import math
import re
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from defusedxml.ElementTree import fromstring

NS = 'https://cyberacademy.ly/ns/course-export'
MAX_PACKAGE = 256 * 1024 * 1024
MAX_FILE = 32 * 1024 * 1024
TEXT = ['title','slug','subtitle','description','level','language','currency','thumbnailUrl']
NUM = ['price','originalPrice','durationHours']
BOOL = ['isPublished','isFeatured','isFree','certificationIncluded']
LISTS = ['tags','requirements','objectives']
LTEXT = ['title','slug','description','content','headerImage','videoUrl']
LNUM = ['durationMinutes','sortOrder']

def slugify(s):
    return re.sub(r'[^\w]+', '-', s.lower(), flags=re.UNICODE).strip('-') or 'course'

def number(value):
    n = float(value)
    if not math.isfinite(n) or n < 0:
        raise ValueError('Numbers must be finite and nonnegative')
    return n

def boolean(value):
    if str(value).lower() not in ('true','false','1','0'):
        raise ValueError('Booleans must be true or false')
    return str(value).lower() in ('true','1')

def parse_package(data):
    if len(data) > MAX_PACKAGE:
        raise ValueError('Package exceeds 256 MB')
    root = fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    if root.tag != '{'+NS+'}cyberacademy-course' or root.get('formatVersion') != '1.0':
        raise ValueError('Expected CyberAcademy course XML namespace and formatVersion 1.0')
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > 256: raise ValueError('XML nesting exceeds 256 levels')
        stack.extend((child, depth+1) for child in node)
    for node in root.iter():
        if not node.tag.startswith('{'+NS+'}'):
            raise ValueError('Unexpected XML namespace')
        node.tag = node.tag.split('}',1)[1]
    if len(root.findall('course')) != 1:
        raise ValueError('Exactly one course is required')
    def fields(node, texts, nums, bools):
        result = {}
        for key in texts+nums+bools:
            el = node.find(key)
            if el is not None:
                value = el.text or ''
                result[key] = number(value) if key in nums else boolean(value) if key in bools else value
        return result
    cnode = root.find('course')
    course = fields(cnode, TEXT, NUM, BOOL)
    if not course.get('title','').strip(): raise ValueError('Course title is required')
    for key in LISTS:
        course[key] = [el.text or '' for el in cnode.findall(key+'/'+('tag' if key=='tags' else 'item'))]
    for key, keys in [('category',['name','slug']),('instructor',['email','fullName'])]:
        el = cnode.find(key)
        if el is not None: course[key] = fields(el, keys, [], [])
    lessons = []
    for node in root.findall('lessons/lesson'):
        lesson = fields(node, LTEXT, LNUM, ['isPublished'])
        if not lesson.get('title','').strip(): continue
        lesson['lab'] = fields(node.find('lab'), ['imageUrl','instructions'], [], []) if node.find('lab') is not None else {}
        lesson['quiz'] = []
        for q in node.findall('quiz/question'):
            question = fields(q, ['prompt','explanation'], [], [])
            question['options'] = [{'text':o.text or '', 'correct':boolean(o.get('correct','false'))} for o in q.findall('options/option')]
            lesson['quiz'].append(question)
        lesson['resources'] = []
        for r in node.findall('resources/resource'):
            resource = fields(r, ['title','url','fileName'], ['fileSize'], [])
            resource['type'] = r.get('type','link')
            f = r.find('file')
            if f is not None:
                if f.get('encoding') != 'base64': raise ValueError('Unsupported file encoding')
                encoded = re.sub(r'\s','',f.text or '')
                if len(encoded) < ((MAX_FILE+2)//3)*4:
                    try: content = base64.b64decode(encoded, validate=True)
                    except Exception as exc: raise ValueError('Invalid base64 file') from exc
                    if len(content) < MAX_FILE:
                        resource['file'] = {'data':base64.b64encode(content).decode(), 'mimeType':f.get('mimeType','application/octet-stream')}
                        resource['fileSize'] = len(content)
            lesson['resources'].append(resource)
        lessons.append(lesson)
    return {'course':course,'lessons':lessons}

def serialize_package(pkg):
    root = ET.Element('cyberacademy-course', {'xmlns':NS,'formatVersion':'1.0','generator':'CyberAcademy Admin','exportedAt':datetime.now(timezone.utc).isoformat()})
    def fields(parent, obj, keys):
        for key in keys:
            if obj.get(key) is not None:
                ET.SubElement(parent,key).text = str(obj[key]).lower() if isinstance(obj[key],bool) else str(obj[key])
    c = pkg['course']; node = ET.SubElement(root,'course')
    fields(node,c,TEXT+NUM+BOOL)
    for key, keys in [('category',['name','slug']),('instructor',['email','fullName'])]:
        fields(ET.SubElement(node,key), c.get(key,{}) or {}, keys)
    for key in LISTS:
        parent = ET.SubElement(node,key)
        for value in c.get(key,[]): ET.SubElement(parent,'tag' if key=='tags' else 'item').text = value
    parent = ET.SubElement(root,'lessons')
    for lesson in pkg['lessons']:
        node = ET.SubElement(parent,'lesson'); fields(node,lesson,LTEXT+LNUM+['isPublished'])
        fields(ET.SubElement(node,'lab'),lesson.get('lab',{}),['imageUrl','instructions'])
        quiz = ET.SubElement(node,'quiz')
        for q in lesson.get('quiz',[]):
            qnode = ET.SubElement(quiz,'question'); fields(qnode,q,['prompt','explanation'])
            options = ET.SubElement(qnode,'options')
            for o in q.get('options',[]): ET.SubElement(options,'option',{'correct':'true'} if o.get('correct') else {}).text = o.get('text','')
        resources = ET.SubElement(node,'resources')
        for r in lesson.get('resources',[]):
            rnode = ET.SubElement(resources,'resource',{'type':r.get('type','link')})
            copy = dict(r)
            if r.get('file'): copy.pop('url',None)
            fields(rnode,copy,['title','url','fileName','fileSize'])
            if r.get('file'):
                ET.SubElement(rnode,'file',{'encoding':'base64','mimeType':r['file'].get('mimeType','application/octet-stream')}).text = r['file']['data']
    ET.indent(root)
    data = ET.tostring(root,encoding='utf-8',xml_declaration=True)
    if len(data)>MAX_PACKAGE: raise ValueError('Package exceeds 256 MB')
    return data
