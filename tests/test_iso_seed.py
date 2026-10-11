import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from app import create_app
from course_xml import parse_package
from scripts.seed_iso_course import seed

class ISOSeedTests(unittest.TestCase):
    def test_seed_portability_and_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            database=Path(folder)/'courses.sqlite'
            app=create_app(str(database));cid=seed(database)
            client=app.test_client();token=client.get('/api/session').json['csrf']
            response=client.post('/api/auth/setup',json={'email':'test@example.com','password':'testing-password-123'},headers={'X-CSRF-Token':token})
            headers={'X-CSRF-Token':response.json['csrf']}
            listing=client.get('/api/courses').json
            self.assertEqual(len(listing),1);self.assertEqual(listing[0]['course']['durationHours'],12.75)
            exported=client.get('/api/admin/course-packages/export?courseId='+cid)
            self.assertEqual(exported.status_code,200)
            pkg=parse_package(exported.data)
            self.assertEqual(len(pkg['lessons']),10)
            self.assertEqual(sum(len(l['quiz']) for l in pkg['lessons']),30)
            for lesson in pkg['lessons']:
                self.assertTrue(lesson['lab']['instructions'])
                self.assertTrue(any(r.get('url')=='https://www.iso27001security.com/' for r in lesson['resources']))
                self.assertEqual(sum(bool(r.get('file')) for r in lesson['resources']),1)
            response=client.post('/api/admin/course-packages/import',data={'file':(io.BytesIO(exported.data),'course.xml'),'replace':'true'},headers=headers)
            self.assertEqual(response.status_code,200);self.assertEqual(response.json['lessonsUpdated'],10);self.assertEqual(response.json['files'],10);self.assertEqual(response.json['removedLessons'],0)
            with sqlite3.connect(database) as db:
                saved=json.loads(db.execute('SELECT data FROM courses WHERE id=?',(cid,)).fetchone()[0]);saved['course']['subtitle']='User edit'
                db.execute('UPDATE courses SET data=? WHERE id=?',(json.dumps(saved),cid))
            self.assertEqual(seed(database),cid)
            self.assertEqual(client.get('/api/courses').json[0]['course']['subtitle'],'User edit')
