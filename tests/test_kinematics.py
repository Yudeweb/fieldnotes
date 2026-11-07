import json
import math
import secrets
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kinematics'))
from content import BOSS, CHECKPOINTS, public_level
from server import grade, make_server


class KinematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.server=make_server(0,Path(cls.tmp.name)/'test.sqlite',Path(cls.tmp.name)/'uploads')
        setup=json.loads(cls.server.auth.setup_file.read_text())['token']
        cls.server.auth.setup({'token':setup,'name':'Test owner','email':'owner@example.test','password':'test-only-owner-password'},'old-browser')
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()

    def setUp(self):
        import http.cookiejar
        self.client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.request('/api/auth/register',{'name':'Test student','email':secrets.token_hex(8)+'@example.test','password':'test-only-student-password'})

    def student_client(self):
        import http.cookiejar
        client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.request('/api/auth/register',{'name':'Another student','email':secrets.token_hex(8)+'@example.test','password':'test-only-student-password'},client)
        return client

    def admin_login(self):
        self.request('/api/auth/logout',{})
        status,_=self.request('/api/auth/login',{'email':'owner@example.test','password':'test-only-owner-password'})
        self.assertEqual(status,200)

    def request(self,path,data=None,client=None):
        headers={'X-Local-Request':'1','Content-Type':'application/json'}
        request=urllib.request.Request(self.url+path, data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:
            with (client or self.client).open(request) as response:return response.status,json.load(response)
        except urllib.error.HTTPError as e:
            with e:return e.code,json.load(e)

    def test_no_answer_key_in_public_content(self):
        def walk(value):
            if isinstance(value,dict):
                self.assertFalse(set(value)&{'answer','tolerance','solution','hints'})
                for v in value.values():walk(v)
            if isinstance(value,list):
                for v in value:walk(v)
        walk(public_level())

    def test_turning_point_distance_is_not_displacement(self):
        g=grade(CHECKPOINTS['cp2'],{'velocity':'-25','displacement':'-77','distance':'77'})
        self.assertEqual(g['correct'],2)
        g=grade(CHECKPOINTS['cp2'],{'velocity':-25,'displacement':-77,'distance':79.25})
        self.assertEqual(g['correct'],3)

    def test_nonfinite_and_expressions_not_evaluated(self):
        for raw in ('NaN','inf','7/5','__import__("os").getcwd()',True):
            result=grade(CHECKPOINTS['cp1'],{'distance':raw})
            self.assertFalse(result['fields'][0]['correct'])

    def test_xp_is_idempotent_and_progress_survives_new_connection(self):
        self.request('/api/level')
        data={'id':'cp1','answers':{'distance':7,'displacement':5,'speed':1.4}}
        _,a=self.request('/api/check',data)
        _,b=self.request('/api/check',data)
        self.assertEqual(a['state']['xp'],20)
        self.assertEqual(b['state']['xp'],20)
        _,s=self.request('/api/state');self.assertEqual(s['xp'],20)

    def test_browser_sessions_are_isolated(self):
        self.request('/api/notes',{'notes':'Private local note'})
        other=self.student_client()
        _,s=self.request('/api/state',client=other)
        self.assertEqual(s['notes'],'')

    def test_assisted_practice_is_recorded(self):
        self.request('/api/hint',{'id':'cp1'})
        _,r=self.request('/api/check',{'id':'cp1','answers':{'distance':7,'displacement':5,'speed':1.4}})
        self.assertTrue(r['assisted']);self.assertEqual(r['state']['xp'],10)

    def test_simulation_withholds_hints_and_feedback_then_locks_submission(self):
        _,b=self.request('/api/boss/start',{'mode':'simulation'})
        self.assertNotIn('feedback',b)
        status,_=self.request('/api/boss/hint',{'id':b['id'],'question':'trajectories'})
        self.assertEqual(status,400)
        answers={'trajectories':{'angle':5.6,'x':2.5,'y':6.25,'range':5/3,'speed':math.sqrt(127.4)},
                 'orbit':{'speed':7480,'acceleration':7.993}}
        _,saved=self.request('/api/boss/save',{'id':b['id'],'answers':answers})
        self.assertNotIn('feedback',saved)
        _,result=self.request('/api/boss/submit',{'id':b['id'],'answers':answers})
        self.assertEqual(result['grade']['correct'],7)
        _,again=self.request('/api/boss/submit',{'id':b['id'],'answers':{}})
        self.assertEqual(again['grade']['correct'],7)
        self.assertEqual(again['state']['xp'],80)

    def test_another_session_cannot_read_boss_attempt(self):
        _,b=self.request('/api/boss/start',{'mode':'practice'})
        status,_=self.request('/api/boss/'+b['id'],client=self.student_client())
        self.assertEqual(status,404)

    def test_expired_simulation_uses_saved_work_not_late_answers(self):
        _,b=self.request('/api/boss/start',{'mode':'simulation'})
        # This test-created attempt has no saved answers when its deadline passes.
        with self.server.store.connect() as db:
            rows=db.execute('SELECT session,payload FROM state').fetchall()
            for sid,payload in rows:
                s=json.loads(payload)
                if b['id'] in s['bosses']:
                    s['bosses'][b['id']]['deadline']=1
                    db.execute('UPDATE state SET payload=? WHERE session=?',(json.dumps(s),sid))
        _,result=self.request('/api/boss/submit',{'id':b['id'],'answers':{'trajectories':{'x':2.5,'y':6.25}}})
        self.assertTrue(result['grade']['expired'])
        self.assertEqual(result['grade']['correct'],0)

    def test_sources_are_allowlisted(self):
        status,_=self.request('/source/mar03/999')
        self.assertEqual(status,404)
        status,_=self.request('/source/solutions/1')
        self.assertEqual(status,404)
        status,_=self.request('/.env')
        self.assertEqual(status,404)

    def test_post_requires_application_header(self):
        request=urllib.request.Request(self.url+'/api/notes',data=b'{"notes":"x"}',headers={'Content-Type':'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code,403)
        caught.exception.close()

    def upload(self,course,filename='slides.pdf',body=b'%PDF-1.4\n% local test source\n%%EOF',client=None,kind='lecture'):
        from urllib.parse import urlencode
        query=urlencode({'filename':filename,'kind':kind,'solutions':'false'})
        request=urllib.request.Request(self.url+f'/api/studio/courses/{course}/documents?{query}',data=body,headers={'X-Local-Request':'1','Content-Type':'application/octet-stream'})
        try:
            with (client or self.client).open(request) as response:return response.status,json.load(response)
        except urllib.error.HTTPError as e:
            with e:return e.code,json.load(e)

    def create_course(self):
        self.admin_login()
        status,course=self.request('/api/studio/courses',{'title':'Physics I test','code':'PHY-1','language':'English','description':'Kinematics source review'})
        self.assertEqual(status,201)
        return course

    def test_course_map_has_only_one_playable_level(self):
        _,course=self.request('/api/course')
        self.assertEqual([l['id'] for l in course['levels'] if l['status']=='available'],['kinematics'])
        self.assertEqual(next(l['status'] for l in course['levels'] if l['id']=='fluids'),'source_gap')

    def test_create_draft_and_upload_private_document(self):
        course=self.create_course()
        status,document=self.upload(course['id'])
        self.assertEqual(status,201)
        self.assertEqual(document['status'],'stored_pending_review')
        _,saved=self.request('/api/studio/courses/'+course['id'])
        self.assertEqual(saved['status'],'draft')
        self.assertEqual(len(saved['documents']),1)
        self.assertTrue((Path(self.tmp.name)/'uploads'/(document['id']+'.pdf')).is_file())
        status,_=self.request('/uploads/'+document['id']+'.pdf')
        self.assertEqual(status,404)

    def test_course_drafts_and_uploads_are_admin_only(self):
        course=self.create_course();self.upload(course['id'])
        other=self.student_client()
        status,_=self.request('/api/studio/courses/'+course['id'],client=other)
        self.assertEqual(status,403)
        status,_=self.request('/api/studio/courses',client=other)
        self.assertEqual(status,403)
        status,_=self.upload(course['id'],client=other)
        self.assertEqual(status,403)

    def test_upload_rejects_spoofed_type_path_and_duplicates(self):
        course=self.create_course()
        for filename,body in [('bad.pdf',b'<script>alert(1)</script>'),('../escape.pdf',b'%PDF-1.4'),('bad.exe',b'%PDF-1.4'),('not.pptx',b'not a zip')]:
            status,_=self.upload(course['id'],filename,body)
            self.assertEqual(status,400)
        self.assertEqual(self.upload(course['id'])[0],201)
        self.assertEqual(self.upload(course['id'])[0],400)

    def test_solution_category_cannot_drop_restricted_flag(self):
        course=self.create_course();_,document=self.upload(course['id'],kind='solution')
        self.assertTrue(document['contains_solutions'])
        status,result=self.request(f"/api/studio/courses/{course['id']}/documents/{document['id']}/classify",{'kind':'solution','contains_solutions':False})
        self.assertEqual(status,200);self.assertTrue(result['contains_solutions'])

    def test_deep_page_routes_load_application_shell(self):
        self.admin_login()
        for path in ('/','/course/physics-1','/levels/kinematics','/studio'):
            with self.client.open(self.url+path) as response:
                self.assertEqual(response.status,200)
                self.assertIn(b'/portal.js',response.read())

    def mock_tutor(self):
        tutor=self.server.tutor
        old_config,old_transport=tutor.config,tutor.transport
        self.addCleanup(setattr,tutor,'config',old_config)
        self.addCleanup(setattr,tutor,'transport',old_transport)
        tutor.config=lambda:{'key':'fake-test-key','enabled':True,'model':'gpt-6-luna','session_cap':.1,'day_cap':.25,'month_cap':2}
        tutor.transport=lambda key,body:{'status':'completed','usage':{'input_tokens':100,'output_tokens':20},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'answer':'Start by distinguishing distance from displacement.','citations':[]})}]}]}

    def test_tutor_endpoint_private_and_checkpoint_help_recorded(self):
        self.mock_tutor();self.request('/api/state')
        message={'id':'integration-message-0001','message':'Give me a hint','context':{'page':'level','section':'practice','lesson':'describe','checkpoint':'cp1'}}
        status,result=self.request('/api/tutor/messages',message)
        self.assertEqual(status,200);self.assertIn('distance',result['answer'])
        _,history=self.request('/api/tutor');self.assertEqual(len(history['messages']),1)
        _,other=self.request('/api/tutor',client=self.student_client());self.assertEqual(other['messages'],[])
        _,grade=self.request('/api/check',{'id':'cp1','answers':{'distance':7,'displacement':5,'speed':1.4}})
        self.assertTrue(grade['assisted']);self.assertEqual(grade['state']['xp'],10)
        _,attempt=self.request('/api/boss/start',{'mode':'simulation'})
        _,blocked=self.request('/api/tutor/messages',message|{'id':'integration-message-0002','context':{'page':'course'}})
        self.assertTrue(blocked['blocked'])
        _,history=self.request('/api/tutor');self.assertTrue(history['status']['paused']);self.assertEqual(history['messages'],[])

    def test_tutor_cannot_access_another_sessions_course_metadata(self):
        self.mock_tutor();course=self.create_course()
        message={'id':'studio-context-test-0001','message':'Describe this course draft','context':{'page':'studio','course':course['id']}}
        status,_=self.request('/api/tutor/messages',message,client=self.student_client())
        self.assertEqual(status,403)
        status,result=self.request('/api/tutor/messages',message)
        self.assertEqual(status,200);self.assertIn('answer',result)


if __name__=='__main__':unittest.main()
