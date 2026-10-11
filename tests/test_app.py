import base64
import io
import tempfile
import unittest
from app import create_app
from course_xml import NS,parse_package,serialize_package

class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.app=create_app(self.temp.name+'/test.sqlite');self.client=self.app.test_client()
        self.csrf=self.client.get('/api/session').json['csrf']
        r=self.client.post('/api/auth/setup',json={'email':'admin@example.com','password':'long-test-password'},headers=self.headers())
        self.csrf=r.json['csrf']
    def tearDown(self): self.temp.cleanup()
    def headers(self): return {'X-CSRF-Token':self.csrf}
    def post(self,url,data): return self.client.post(url,json=data,headers=self.headers())
    def package(self):
        return {'course':{'title':'Web & Security','description':'<p>text ]]> & special</p>','tags':['security'],'instructor':{'email':'admin@example.com','fullName':'Admin'}},'lessons':[{'title':'HTTP','slug':'http','content':'content & <tag>','durationMinutes':90,'lab':{'instructions':'Use curl'},'quiz':[{'prompt':'Header?','options':[{'text':'Length','correct':True},{'text':'Other','correct':False}],'explanation':'Because'}],'resources':[{'type':'pdf','title':'Guide','fileName':'guide.pdf','file':{'data':base64.b64encode(b'%PDF-test').decode(),'mimeType':'application/pdf'}}]}]}
    def import_xml(self,data,replace=False):return self.client.post('/api/admin/course-packages/import',data={'file':(io.BytesIO(data),'course.xml'),'replace':str(replace).lower()},headers=self.headers())
    def test_crud_and_permissions(self):
        anon=self.app.test_client();self.assertEqual(anon.get('/api/courses').status_code,401)
        self.assertEqual(self.client.post('/api/courses',json=self.package()).status_code,403)
        r=self.post('/api/courses',self.package());self.assertEqual(r.status_code,201);cid=r.json['id']
        data=r.json;data['course']['title']='Edited';data['course']['slug']='changed'
        r=self.client.put('/api/courses/'+cid,json=data,headers=self.headers());self.assertEqual(r.json['course']['slug'],'web-security')
        self.assertEqual(r.json['course']['title'],'Edited')
        self.assertEqual(self.client.delete('/api/courses/'+cid,headers=self.headers()).status_code,200)
        self.assertEqual(self.client.get('/api/courses').json,[])
    def test_round_trip(self):
        r=self.import_xml(serialize_package(self.package()));self.assertEqual(r.status_code,200);self.assertEqual(r.json['files'],1)
        cid=r.json['courseId'];export=self.client.get('/api/admin/course-packages/export?courseId='+cid)
        pkg=parse_package(export.data);self.assertEqual(pkg['lessons'][0]['resources'][0]['file']['data'],base64.b64encode(b'%PDF-test').decode())
        self.assertEqual(pkg['course']['description'],self.package()['course']['description'])
        r=self.import_xml(export.data,True);self.assertFalse(r.json['created']);self.assertEqual(r.json['lessonsUpdated'],1);self.assertEqual(r.json['removedLessons'],0)
        course=self.client.get('/api/courses').json[0];l=course['lessons'][0]
        self.assertEqual(self.client.get(f'/api/courses/{cid}/lessons/{l["id"]}/resources/0').data,b'%PDF-test')
        self.assertEqual(course['course']['durationHours'],1.5)
    def test_merge_and_prune(self):
        p=self.package();p['lessons'].append({'title':'Second','slug':'second','durationMinutes':30})
        self.import_xml(serialize_package(p));sparse={'course':{'title':'Web & Security','description':''},'lessons':[]}
        self.import_xml(serialize_package(sparse),True)
        course=self.client.get('/api/courses').json[0];self.assertEqual(len(course['lessons']),2);self.assertTrue(course['course']['description'])
        r=self.import_xml(serialize_package(self.package()),True);self.assertEqual(r.json['removedLessons'],1)
    def test_invalid_import_is_atomic(self):
        self.import_xml(serialize_package(self.package()));before=self.client.get('/api/courses').json
        p=self.package();p['lessons'][0]['resources'][0]['file']['data']='INVALID!'
        self.assertEqual(self.import_xml(serialize_package(p)).status_code,400)
        self.assertEqual(self.client.get('/api/courses').json,before)
        evil=f'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><cyberacademy-course xmlns="{NS}" formatVersion="1.0"><course><title>&e;</title></course></cyberacademy-course>'.encode()
        self.assertEqual(self.import_xml(evil).status_code,400)
        self.assertEqual(self.import_xml(b'<broken>').status_code,400)
        self.assertEqual(self.client.get('/api/admin/course-packages/export?name=missing').status_code,404)
        self.assertEqual(self.client.get('/api/admin/course-packages/export').status_code,400)
    def test_full_model(self):
        p=self.package();p['course'].update(slug='stable',subtitle='Subtitle',level='advanced',language='ar',currency='LYD',price=10,originalPrice=20,durationHours=1,thumbnailUrl='https://example.com/image',isPublished=True,isFeatured=True,isFree=False,certificationIncluded=False,category={'name':'Security','slug':'security'},requirements=['one'],objectives=['two'])
        p['lessons'][0].update(description='desc',headerImage='https://example.com/header',videoUrl='https://example.com/video',sortOrder=2,isPublished=False)
        parsed=parse_package(serialize_package(p))
        self.assertEqual(parsed['course'],p['course']);self.assertEqual(parsed['lessons'][0]['quiz'],p['lessons'][0]['quiz'])

if __name__=='__main__':unittest.main()
