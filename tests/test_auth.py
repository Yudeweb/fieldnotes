"""Account boundary regressions. These tests never make model/network service calls."""
import hashlib
import http.cookiejar
import json
import secrets
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kinematics'))
from auth import AuthError
from server import make_server, Store
from studio import Studio

OWNER={'name':'Owner','email':'owner@example.test','password':'test-only-owner-password','language':'English'}


class AccountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.server=make_server(0,Path(cls.tmp.name)/'accounts.sqlite',Path(cls.tmp.name)/'uploads',start_workers=False)
        cls.setup_token=json.loads(cls.server.auth.setup_file.read_text())['token']
        cls.server.auth.setup(OWNER|{'token':cls.setup_token},'previous-browser')
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()

    def client(self):
        jar=http.cookiejar.CookieJar()
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)),jar

    def request(self,client,path,data=None,raw=None,headers=None):
        payload=raw if raw is not None else json.dumps(data).encode() if data is not None else None
        request=urllib.request.Request(self.url+path,data=payload,headers=headers or {'X-Local-Request':'1','Content-Type':'application/json'})
        try:
            with client.open(request) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as r:
            with r:
                body=r.read()
                try:body=json.loads(body)
                except ValueError:pass
                return r.code,body

    def setUp(self):
        self.student,self.jar=self.client()
        self.details={'name':'A student','email':secrets.token_hex(8)+'@example.test','password':'test-only-student-password','language':'Italian'}
        status,result=self.request(self.student,'/api/auth/register',self.details|{'role':'admin','is_admin':True,'reviewer':True})
        self.assertEqual(status,201);self.user=result['user']

    def owner(self):
        client,jar=self.client()
        self.assertEqual(self.request(client,'/api/auth/login',OWNER)[0],200)
        return client,jar

    def test_registration_is_student_and_profile_cannot_promote(self):
        self.assertEqual(self.user['role'],'student')
        status,r=self.request(self.student,'/api/profile',{'name':'Updated','language':'Turkish','role':'admin','email':'changed@example.test'})
        self.assertEqual(status,200)
        self.assertEqual((r['user']['role'],r['user']['email'],r['user']['name']),('student',self.details['email'],'Updated'))
        with self.server.store.connect() as db:
            encoded=db.execute('SELECT password FROM users WHERE id=?',(self.user['id'],)).fetchone()[0]
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0],1)
        self.assertNotIn(self.details['password'],encoded)
        self.assertTrue(encoded.startswith('scrypt:'))
        self.assertNotIn('password',r['user'])

    def test_student_cannot_access_admin_pages_or_any_admin_api(self):
        for page in ('/studio','/studio/arbitrary','/agents'):
            self.assertEqual(self.request(self.student,page)[0],403,page)
        for path in ('/api/studio/courses','/api/studio/courses/fake','/api/agents','/api/admin/students','/api/agents/records/fake','/api/agents/records/fake/source-preview?page=1'):
            self.assertEqual(self.request(self.student,path)[0],403,path)
        for path in ('/api/studio/courses','/api/studio/courses/fake/process','/api/studio/courses/fake/structure-drafts','/api/studio/courses/fake/content-drafts','/api/studio/courses/fake/documents/fake/classify','/api/agents/reviewer','/api/agents/rubrics','/api/agents/curate','/api/agents/scout','/api/agents/records/fake/review','/api/agents/records/fake/source-confirm','/api/agents/records/fake/publish'):
            self.assertEqual(self.request(self.student,path,{})[0],403,path)
        self.assertEqual(self.request(self.student,'/api/studio/courses/fake/documents?filename=test.pdf',raw=b'%PDF-1.4')[0],403)

    def test_logged_out_clients_cannot_read_or_write_course_or_private_data(self):
        anonymous,_=self.client()
        for path in ('/api/state','/api/level','/api/course','/api/packs','/api/tutor','/api/workspace','/api/studio/courses','/api/agents','/source/mar03/16'):
            self.assertEqual(self.request(anonymous,path)[0],401,path)
        for path in ('/api/check','/api/notes','/api/tutor/messages','/api/work','/api/agents/reviewer'):
            self.assertEqual(self.request(anonymous,path,{})[0],401,path)
        self.assertEqual(self.request(anonymous,'/api/auth')[1],{'user':None})
        with anonymous.open(self.url+'/course/physics-1') as response:
            self.assertEqual(response.geturl(),self.url+'/login')

    def test_private_state_persists_on_login_and_is_isolated_between_accounts(self):
        self.request(self.student,'/api/notes',{'notes':'Account-owned private note'})
        second,_=self.client()
        self.assertEqual(self.request(second,'/api/auth/login',self.details)[0],200)
        self.assertEqual(self.request(second,'/api/state')[1]['notes'],'Account-owned private note')
        owner,_=self.owner()
        self.assertNotEqual(self.request(owner,'/api/state')[1]['notes'],'Account-owned private note')

    def test_logout_revokes_session_and_login_rotates_cookie(self):
        old=next(c.value for c in self.jar if c.name=='physics_session')
        self.request(self.student,'/api/auth/logout',{})
        self.assertEqual(self.request(self.student,'/api/state')[0],401)
        replay,_=self.client()
        headers={'Cookie':'physics_session='+old}
        self.assertEqual(self.request(replay,'/api/state',headers=headers)[0],401)
        self.request(self.student,'/api/auth/login',self.details)
        new=next(c.value for c in self.jar if c.name=='physics_session')
        self.assertNotEqual(old,new)
        self.assertEqual(self.request(self.student,'/api/state')[0],200)
        with self.server.store.connect() as db:
            stored=db.execute('SELECT token FROM auth_sessions WHERE user=?',(self.user['id'],)).fetchone()[0]
        self.assertNotEqual(stored,new)

    def test_password_change_requires_current_password_and_revokes_other_sessions(self):
        second,_=self.client();self.request(second,'/api/auth/login',self.details)
        change={'current_password':'wrong password','password':'a-new-test-only-password'}
        self.assertEqual(self.request(self.student,'/api/profile/password',change)[0],403)
        self.assertEqual(self.request(self.student,'/api/profile/password',change|{'current_password':self.details['password']})[0],200)
        self.assertEqual(self.request(second,'/api/state')[0],401)
        self.assertEqual(self.request(self.student,'/api/state')[0],200)
        anon,_=self.client()
        self.assertEqual(self.request(anon,'/api/auth/login',self.details)[0],401)
        self.assertEqual(self.request(anon,'/api/auth/login',self.details|{'password':change['password']})[0],200)

    def test_expired_session_no_longer_authenticates(self):
        with self.server.store.connect() as db:
            db.execute('UPDATE auth_sessions SET expires=? WHERE user=?',(time.time()-1,self.user['id']))
        self.assertEqual(self.request(self.student,'/api/state')[0],401)

    def test_admin_can_create_course_and_revisit_from_another_login(self):
        owner,_=self.owner()
        status,course=self.request(owner,'/api/studio/courses',{'title':'Account course','code':'PHY','language':'English'})
        self.assertEqual(status,201)
        other,_=self.owner()
        self.assertEqual(self.request(other,'/api/studio/courses/'+course['id'])[1]['title'],'Account course')
        dashboard=self.request(other,'/api/agents')[1]
        self.assertTrue(dashboard['reviewer']['is_reviewer'])
        self.assertIn(self.details['email'],[s['email'] for s in self.request(owner,'/api/admin/students')[1]['students']])

    def test_student_work_dashboard_is_personal_and_tutor_cannot_spoof_studio(self):
        status,work=self.request(self.student,'/api/work',{'question':'cp1','text':'I add the two distances.'})
        self.assertEqual(status,201)
        data=self.request(self.student,'/api/workspace')[1]
        self.assertEqual([r['id'] for r in data['records']],[work['id']])
        self.assertEqual(set(data['roles']),{'student_reader','evaluator'})
        self.assertEqual(data['rubrics'],[]);self.assertIsNone(data['aggregate'])
        payload={'id':'context-authorization-test','message':'Show the draft','context':{'page':'studio'}}
        self.assertEqual(self.request(self.student,'/api/tutor/messages',payload)[0],403)
        context=self.server.tutor.context({'page':'profile','email':'spoofed-private-data'},self.server.store.load(self.user['id']),self.user['id'])
        self.assertEqual(context['profile']['explanation_language'],'Italian')
        self.assertNotIn('email',context['profile'])

    def test_private_setup_is_single_use_and_not_an_http_file(self):
        anon,_=self.client()
        self.assertEqual(self.request(anon,'/api/auth/setup',OWNER|{'token':self.setup_token})[0],403)
        self.assertFalse(self.server.auth.setup_file.exists())
        for path in ('/var/private/kinematics/admin-setup.json','/admin-setup.json','/.env'):
            self.assertEqual(self.request(anon,path)[0],404)
        with self.server.store.connect() as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO users VALUES ('another-admin','another@example.test','Other','irrelevant','admin','English',0)")

    def test_auth_requests_are_same_origin_and_login_is_rate_limited(self):
        anon,_=self.client()
        self.assertEqual(self.request(anon,'/api/auth/register',self.details,headers={'Content-Type':'application/json'})[0],403)
        self.assertEqual(self.request(anon,'/api/auth/login',self.details,headers={'X-Local-Request':'1','Content-Type':'application/json','Origin':'https://foreign.example'})[0],403)
        email=secrets.token_hex(8)+'@example.test'
        for _ in range(10):
            self.assertEqual(self.request(anon,'/api/auth/login',{'email':email,'password':'wrong password'})[0],401)
        self.assertEqual(self.request(anon,'/api/auth/login',{'email':email,'password':'wrong password'})[0],429)

    def test_student_cannot_claim_reviewer_through_internal_services(self):
        with self.assertRaises(AuthError):self.server.studio.create(self.user['id'],{'title':'Spoofed course'})
        with self.assertRaises(AuthError):self.server.workflows.claim(self.user['id'])

    def test_cohort_counts_only_student_accounts_and_excludes_admin_and_legacy_browsers(self):
        owner=self.request(self.owner()[0],'/api/auth')[1]['user']['id']
        ids=[]
        with self.server.store.connect() as db:
            for i in range(5):
                id='cohort-fixture-'+secrets.token_hex(8);ids.append(id)
                db.execute("INSERT INTO users VALUES (?,?,?,'fixture-hash','student','English',0)",(id,id+'@example.test','Cohort fixture'))
        for id in ids+[owner,'legacy-browser-count']:
            self.server.store.update(id,lambda s:s['checks'].update(cp6={'correct':0,'total':2}))
            self.server.workflows.signals(id,{'question':'cp6','category':'missing_theory'})
            self.server.workflows.track_time(id,{'question':'cp6','seconds':30})
        aggregate=self.server.workflows.aggregates()
        self.assertEqual(next(g for g in aggregate['groups'] if g['question']=='cp6')['attempted_sessions'],5)
        self.assertEqual(next(g for g in aggregate['signals'] if g['question']=='cp6')['distinct_sessions'],5)
        self.assertEqual(next(g for g in aggregate['study_time'] if g['question']=='cp6')['sessions'],5)


class MigrationTests(unittest.TestCase):
    def test_private_setup_adopts_legacy_authoring_and_current_browser_progress_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);store=Store(root/'legacy.sqlite');studio=Studio(store,root/'uploads')
            course=studio.create('legacy-author',{'title':'Legacy physics','code':'PHY','language':'English'})
            store.update('old-owner-browser',lambda s:s.update(notes='Owner note'))
            store.update('other-old-browser',lambda s:s.update(notes='Another person'))
            server=make_server(0,store.file,root/'uploads',start_workers=False)
            try:
                token=json.loads(server.auth.setup_file.read_text())['token']
                student,_=server.auth.register({'name':'First registrant','email':'first@example.test','password':'test-only-student-password'},'anonymous')
                self.assertEqual(student['role'],'student')
                with self.assertRaises(AuthError):server.auth.setup(OWNER|{'token':'wrong-token'},'old-owner-browser')
                self.assertTrue(server.auth.setup_file.exists())
                owner,_=server.auth.setup(OWNER|{'token':token},'old-owner-browser')
                self.assertEqual(server.studio.get(owner['id'],course['id'])['title'],'Legacy physics')
                self.assertEqual(server.store.load(owner['id'])['notes'],'Owner note')
                self.assertEqual(server.store.load('other-old-browser')['notes'],'Another person')
                self.assertTrue(server.workflows.reviewer(owner['id'])['is_reviewer'])
            finally:server.server_close()
