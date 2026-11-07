"""Dependency-free, localhost-only kinematics prototype with bounded AI tutoring."""
import argparse
import hashlib
import json
import math
import mimetypes
import secrets
import sqlite3
import time
from contextlib import contextmanager
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from content import BOSS, CHECKPOINTS, SOURCES, public_level
from catalogue import course_catalogue
from studio import MAX_UPLOAD, Studio, StudioError
from ai import Tutor, AIError
from agents import Workflows, WorkflowError
from auth import Accounts, AuthError, SESSION_SECONDS

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'var/private/kinematics'
WEB = ROOT / 'web'


class Invalid(ValueError):
    pass


def grade(question, answers):
    if not isinstance(answers, dict):
        raise Invalid('Answers must be an object.')
    results = []
    for f in question['fields']:
        raw = answers.get(f['id'], '')
        try:
            if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
                raise ValueError()
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError()
            correct = abs(value - f['answer']) <= f['tolerance'] + 1e-12
        except (ValueError, TypeError, OverflowError):
            correct = False
        results.append({'id':f['id'],'correct':correct})
    return {'fields':results,'correct':sum(x['correct'] for x in results),'total':len(results)}


class Store:
    def __init__(self, file):
        self.file = file
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS state (session TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        Path(file).chmod(0o600)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.file, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def load(self, session):
        with self.connect() as db:
            row=db.execute('SELECT payload FROM state WHERE session=?',(session,)).fetchone()
        return json.loads(row[0]) if row else {'completed':[], 'hints':{},'checks':{},'xp_events':{},'bosses':{},'notes':'','feedback':[]}

    def update(self, session, action):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT payload FROM state WHERE session=?',(session,)).fetchone()
            s=json.loads(row[0]) if row else self.load(session)
            result=action(s)
            db.execute('INSERT OR REPLACE INTO state VALUES (?,?)',(session,json.dumps(s)))
        return result


def state_view(s):
    return {'completed':s['completed'],'checks':s['checks'],'xp':sum(s['xp_events'].values()),'notes':s['notes'],
            'bosses':[{'id':id,'mode':b['mode'],'submitted':b.get('submitted',False),'grade':b.get('grade'),'started':b['started']} for id,b in s['bosses'].items()]}


def boss_view(id, b):
    out={'id':id,'mode':b['mode'],'started':b['started'],'deadline':b['deadline'],'answers':b['answers'],'submitted':b.get('submitted',False)}
    if b.get('submitted'):
        out['grade']=b['grade'];out['feedback']=b['feedback']
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Do not log query strings, cookies or submissions.
        pass

    def valid_host(self):
        return self.headers.get('Host') in (f'localhost:{self.server.server_port}',f'127.0.0.1:{self.server.server_port}')

    def session(self):
        cookie=cookies.SimpleCookie()
        try: cookie.load(self.headers.get('Cookie',''))
        except cookies.CookieError: pass
        token=cookie.get('physics_session')
        token=token.value if token else ''
        if len(token)!=64 or any(c not in '0123456789abcdef' for c in token):
            token=secrets.token_hex(32);self.new_cookie=token
        return hashlib.sha256(token.encode()).hexdigest()

    def send(self, status, data, content_type='application/json; charset=utf-8'):
        if not isinstance(data, bytes): data=json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if getattr(self,'new_cookie',None):
            self.send_header('Set-Cookie',f'physics_session={self.new_cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_SECONDS}')
        self.end_headers();self.wfile.write(data)

    def redirect(self, location):
        self.send_response(303)
        self.send_header('Location',location)
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length','0')
        self.end_headers()

    def access(self, path, user):
        if not user:
            raise AuthError('Sign in to continue.',401)
        if path.startswith(('/api/studio','/api/agents','/api/admin')):
            self.server.auth.require_admin(user['id'])
        return user['id']

    def do_GET(self):
        self.new_cookie=None
        if not self.valid_host(): return self.send(403,{'error':'Local host required.'})
        token_hash=self.session();path=urlparse(self.path).path
        user=self.server.auth.current(token_hash)
        if path=='/api/auth':return self.send(200,{'user':user})
        if path.startswith(('/api/','/source/')):
            try:sid=self.access(path,user)
            except AuthError as e:return self.send(e.status,{'error':str(e)})
        else:sid=user['id'] if user else None
        protected_page=path in ('/','/course/physics-1','/levels/kinematics','/agents','/work','/profile') or path=='/studio' or path.startswith('/studio/')
        if protected_page and not user:return self.redirect('/login')
        if user and path in ('/login','/register'):return self.redirect('/course/physics-1')
        if (path=='/agents' or path=='/studio' or path.startswith('/studio/')) and user['role']!='admin':
            return self.send(403,b'<!doctype html><title>Administrator access required</title><h1>This workspace is for the administrator.</h1><p><a href="/course/physics-1">Return to your course</a></p>','text/html; charset=utf-8')
        try:
            if path=='/api/admin/students':return self.send(200,{'students':self.server.auth.students()})
            if path=='/api/workspace':return self.send(200,self.server.workflows.dashboard(sid,personal=True))
            if path=='/api/agents':return self.send(200,self.server.workflows.dashboard(sid))
            if path.startswith('/api/jobs/'):return self.send(200,self.server.workflows.job(sid,path.split('/')[-1]))
            if path.startswith('/api/agents/records/'):
                if path.endswith('/source-preview'):return self.send(200,self.server.workflows.source_preview(sid,path.split('/')[4],int(parse_qs(urlparse(self.path).query).get('page',['1'])[0])))
                return self.send(200,self.server.workflows.record(sid,path.split('/')[-1]))
            if path=='/api/packs':return self.send(200,{'packs':self.server.workflows.packs(),'resources':self.server.workflows.public_resources(),'faqs':self.server.workflows.public_faqs()})
            if path.startswith('/api/packs/'):
                parts=path.split('/')
                if len(parts)==7 and parts[4]=='source':return self.send(200,self.server.workflows.published_source(parts[3],parts[5],int(parts[6])))
                if len(parts)==4:return self.send(200,self.server.workflows.published(parts[3]))
            if path.startswith('/api/work/') and path.endswith('/preview'):
                file=self.server.workflows.work_file(sid,path.split('/')[3])
                return self.send(200,self.server.workflows.extractor(file,student=True))
        except (WorkflowError,StudioError,ValueError) as e:return self.send(404,{'error':str(e)})
        if path=='/api/course': return self.send(200,course_catalogue())
        if path=='/api/studio/courses': return self.send(200,{'courses':self.server.studio.list(sid)})
        if path.startswith('/api/studio/courses/'):
            try: return self.send(200,self.server.studio.get(sid,path.split('/')[-1]))
            except StudioError as e:return self.send(404,{'error':str(e)})
        if path=='/api/level': return self.send(200,public_level())
        if path=='/api/state': return self.send(200,state_view(self.server.store.load(sid)))
        if path=='/api/tutor':
            paused=any(b['mode']=='simulation' and not b['submitted'] for b in self.server.store.load(sid)['bosses'].values())
            return self.send(200,{'status':self.server.tutor.status(sid)|{'paused':paused},'messages':[] if paused else self.server.tutor.history(sid)})
        if path.startswith('/api/boss/'):
            id=path.split('/')[-1];b=self.server.store.load(sid)['bosses'].get(id)
            return self.send(200,boss_view(id,b)) if b else self.send(404,{'error':'Attempt not found.'})
        if path.startswith('/source/'):
            parts=path.split('/')
            if len(parts)!=4:return self.send(404,{'error':'Source not found.'})
            key=parts[2]
            try:page=int(parts[3])
            except ValueError:return self.send(404,{'error':'Source not found.'})
            if key not in SOURCES or page not in SOURCES[key]['pages']:return self.send(404,{'error':'Source not found.'})
            file=DATA/'source-pages'/f'{key}-{page}.png'
            if not file.is_file():return self.send(404,{'error':'Run the source-preview preparation script first.'})
            return self.send(200,file.read_bytes(),'image/png')
        assets={'/':'index.html','/course/physics-1':'index.html','/levels/kinematics':'index.html','/studio':'index.html','/agents':'index.html','/work':'index.html','/profile':'index.html','/login':'index.html','/register':'index.html','/setup':'index.html','/auth.js':'auth.js','/auth.css':'auth.css','/app.js':'app.js','/portal.js':'portal.js','/tutor.js':'tutor.js','/game.js':'game.js','/agents.js':'agents.js','/agents.css':'agents.css','/style.css':'style.css','/portal.css':'portal.css','/game.css':'game.css','/tutor.css':'tutor.css'}
        if path.startswith('/studio/') and len(path.split('/'))==3: assets[path]='index.html'
        if path in assets:
            f=WEB/assets[path]
            return self.send(200,f.read_bytes(),mimetypes.guess_type(f)[0] or 'application/octet-stream')
        return self.send(404,{'error':'Not found.'})

    def do_POST(self):
        self.new_cookie=None
        if not self.valid_host() or self.headers.get('X-Local-Request')!='1':
            return self.send(403,{'error':'Local application request required.'})
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://localhost:{self.server.server_port}',f'http://127.0.0.1:{self.server.server_port}'):
            return self.send(403,{'error':'Origin not allowed.'})
        try:
            token_hash=self.session();parsed=urlparse(self.path);path=parsed.path
            user=self.server.auth.current(token_hash)
            if path in ('/api/auth/register','/api/auth/login','/api/auth/setup','/api/auth/logout'):
                length=int(self.headers.get('Content-Length','0'))
                if length<=0 or length>8000:raise Invalid('Invalid account request size.')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict):raise Invalid('Expected an object.')
                if path=='/api/auth/logout':
                    self.server.auth.logout(token_hash);self.new_cookie=secrets.token_hex(32)
                    return self.send(200,{'signed_out':True})
                if user:raise AuthError('Sign out before using a different account.',409)
                action=path.split('/')[-1]
                email=data.get('email','')
                self.server.auth.limit(action,self.client_address[0],email[:254].strip().casefold() if isinstance(email,str) else '')
                account,self.new_cookie=getattr(self.server.auth,action)(data,token_hash)
                return self.send(201 if action!='login' else 200,{'user':account})
            sid=self.access(path,user)
            length=int(self.headers.get('Content-Length','0'))
            if path=='/api/work/upload':
                if length<=0 or length>8*1024*1024:raise Invalid('Student work must be up to 8 MB.')
                query=parse_qs(parsed.query)
                return self.send(201,self.server.workflows.upload_work(sid,query.get('filename',[''])[0],query.get('question',[''])[0],query.get('attempt',[None])[0],self.rfile.read(length)))
            if path.startswith('/api/studio/courses/') and path.endswith('/documents'):
                if length<=0 or length>MAX_UPLOAD:raise Invalid('Each upload must be between 1 byte and 25 MB.')
                if len(path.split('/'))!=6:raise Invalid('Invalid upload route.')
                query=parse_qs(parsed.query)
                course=path.split('/')[4]
                # Check ownership before receiving/storing any file bytes.
                self.server.studio.get(sid,course)
                body=self.rfile.read(length)
                if len(body)!=length:raise Invalid('The upload was interrupted.')
                record=self.server.studio.upload(sid,course,query.get('filename',[''])[0],query.get('kind',['lecture'])[0],query.get('solutions',['false'])[0]=='true',body)
                return self.send(201,record)
            if length<0 or length>64000:raise Invalid('Request is too large.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise Invalid('Expected an object.')
            if path=='/api/profile':return self.send(200,{'user':self.server.auth.update(sid,data)})
            if path=='/api/profile/password':
                self.server.auth.limit('password',self.client_address[0],user['email'])
                self.new_cookie=self.server.auth.change_password(sid,data)
                return self.send(200,{'saved':True})
            if path=='/api/agents/reviewer':return self.send(200,self.server.workflows.claim(sid))
            if path=='/api/agents/rubrics':return self.send(201,self.server.workflows.approve_rubric(sid,data))
            if path=='/api/agents/curate':return self.send(202,self.server.workflows.queue(sid,'curator',data))
            if path=='/api/agents/scout':return self.send(202,self.server.workflows.queue(sid,'scout',data,data.get('course','')))
            if path=='/api/work':return self.send(201,self.server.workflows.typed_work(sid,data))
            if path=='/api/signals':return self.send(200,self.server.workflows.signals(sid,data))
            if path=='/api/signals/time':return self.send(200,self.server.workflows.track_time(sid,data))
            if path.startswith('/api/work/'):
                parts=path.split('/')
                if len(parts)!=5:raise Invalid('Unknown work action.')
                if parts[4]=='confirm':return self.send(200,self.server.workflows.confirm_work(sid,parts[3],data))
                role={'read':'student_reader','evaluate':'evaluator'}.get(parts[4])
                if role:return self.send(202,self.server.workflows.queue(sid,role,data|{'work':parts[3]}))
            if path.startswith('/api/evaluations/') and path.endswith('/dispute'):return self.send(201,self.server.workflows.dispute(sid,path.split('/')[3],data))
            if path.startswith('/api/resources/') and path.endswith('/vote'):return self.send(200,self.server.workflows.vote(sid,path.split('/')[3]))
            if path.startswith('/api/agents/records/'):
                parts=path.split('/')
                if len(parts)!=6:raise Invalid('Unknown review action.')
                method={'review':self.server.workflows.review,'source-confirm':self.server.workflows.confirm_source,'publish':self.server.workflows.publish}.get(parts[5])
                if method:return self.send(200,method(sid,parts[4],data))
            if path.startswith('/api/studio/courses/'):
                parts=path.split('/')
                if len(parts)==6 and parts[5] in ('process','structure-drafts','content-drafts'):
                    role={'process':'source_reader','structure-drafts':'builder_structure','content-drafts':'builder_content'}[parts[5]]
                    return self.send(202,self.server.workflows.queue(sid,role,data,parts[4]))
            if path=='/api/tutor/messages':
                result=self.server.tutor.ask(sid,data,self.server.store.load(sid))
                def record_assistance(s):
                    if any(b['mode']=='simulation' and not b['submitted'] for b in s['bosses'].values()):
                        return {'question':data['message'],'answer':'The tutor is paused until your exam simulation is submitted.','citations':[],'blocked':True}
                    context=data.get('context',{})
                    if not result.get('blocked') and context.get('page')=='level':
                        from content import LESSONS
                        lesson=next((l for l in LESSONS if l['id']==context.get('lesson')),None)
                        checkpoint=context.get('checkpoint') or (lesson.get('checkpoint') if lesson else None)
                        if checkpoint in CHECKPOINTS:s['hints'][checkpoint]=max(1,s['hints'].get(checkpoint,0))
                        if context.get('section')=='boss':
                            for b in s['bosses'].values():
                                if b['mode']=='practice' and not b['submitted']:b['hints']['tutor']=1
                    return result
                response=self.server.store.update(sid,record_assistance)
                context=data.get('context',{})
                from content import LESSONS
                lesson=next((l for l in LESSONS if l['id']==context.get('lesson')),None)
                checkpoint=context.get('checkpoint') or (lesson.get('checkpoint') if lesson and context.get('page')=='level' else None)
                if checkpoint in CHECKPOINTS and not response.get('blocked'):
                    self.server.workflows.signals(sid,{'question':checkpoint,'category':'tutor_help'})
                return self.send(200,response)
            if path=='/api/studio/courses':return self.send(201,self.server.studio.create(sid,data))
            if path.startswith('/api/studio/courses/') and path.endswith('/classify'):
                parts=path.split('/')
                if len(parts)!=8:raise Invalid('Invalid document route.')
                result=self.server.studio.classify(sid,parts[4],parts[6],data)
                self.server.workflows.invalidate(parts[4])
                return self.send(200,result)
            result=self.server.store.update(sid,lambda s:self.mutate(path,data,s))
            return self.send(200,result)
        except AuthError as e:
            return self.send(e.status,{'error':str(e)})
        except (Invalid,StudioError,ValueError,TypeError,KeyError) as e:
            return self.send(400,{'error':str(e) if isinstance(e,(Invalid,StudioError,AIError,WorkflowError)) else 'Invalid request.'})

    def mutate(self,path,d,s):
        if path=='/api/complete':
            if d.get('id') not in {l['id'] for l in public_level()['lessons']}:raise Invalid('Unknown lesson.')
            if d['id'] not in s['completed']:s['completed'].append(d['id'])
            return state_view(s)
        if path=='/api/notes':
            if not isinstance(d.get('notes'),str) or len(d['notes'])>12000:raise Invalid('Notes must be under 12,000 characters.')
            s['notes']=d['notes'];return {'saved':True}
        if path in ('/api/hint','/api/check'):
            id=d.get('id');q=CHECKPOINTS.get(id)
            if not q:raise Invalid('Unknown checkpoint.')
            if path=='/api/hint':
                count=s['hints'].get(id,0);s['hints'][id]=count+1
                return {'hint':q['hints'][min(count,len(q['hints'])-1)]}
            g=grade(q,d.get('answers'));assisted=bool(s['hints'].get(id))
            first=id not in s['checks']
            s['checks'][id]={'correct':g['correct'],'total':g['total'],'assisted':assisted,'first_attempt':first}
            all_correct=g['correct']==g['total']
            if all_correct and id not in s['xp_events']:
                # Repeated attempts provide practice evidence, not fresh independent assessment.
                s['xp_events'][id]=20 if first and not assisted else 10
            return g|{'assisted':assisted,'solution':q['solution'],'misconception':q['misconception'],'state':state_view(s)}
        if path=='/api/boss/start':
            mode=d.get('mode')
            if mode not in ('practice','simulation'):raise Invalid('Choose practice or simulation.')
            id=secrets.token_hex(12);now=time.time()
            s['bosses'][id]={'mode':mode,'started':now,'deadline':now+BOSS['minutes']*60 if mode=='simulation' else None,'answers':{},'submitted':False,'hints':{}}
            return boss_view(id,s['bosses'][id])
        if path in ('/api/boss/save','/api/boss/hint','/api/boss/submit'):
            id=d.get('id');b=s['bosses'].get(id)
            if not b:raise Invalid('Attempt not found.')
            if b['submitted']:
                if path=='/api/boss/submit':return boss_view(id,b)|{'state':state_view(s)}
                raise Invalid('This attempt has been submitted.')
            if path=='/api/boss/hint':
                if b['mode']!='practice':raise Invalid('Hints are withheld in exam simulation.')
                q=next((q for q in BOSS['questions'] if q['id']==d.get('question')),None)
                if not q:raise Invalid('Unknown question.')
                n=b['hints'].get(q['id'],0);b['hints'][q['id']]=n+1
                return {'hint':q['hints'][min(n,len(q['hints'])-1)]}
            expired=bool(b['deadline'] and time.time()>b['deadline'])
            # After the deadline only previously autosaved work is assessed.
            if not expired:
                answers=d.get('answers')
                if not isinstance(answers,dict):raise Invalid('Answers must be an object.')
                for q in BOSS['questions']:grade(q,answers.get(q['id'],{}))
                b['answers']=answers
            if path=='/api/boss/save' and not expired:return {'saved':True}
            feedback=[]
            for q in BOSS['questions']:
                g=grade(q,b['answers'].get(q['id'],{}))
                feedback.append({'id':q['id'],**g,'solution':q['solution']})
            correct=sum(f['correct'] for f in feedback);total=sum(f['total'] for f in feedback)
            b.update(submitted=True,feedback=feedback,grade={'correct':correct,'total':total,'assisted':bool(b['hints']),'expired':expired})
            if correct/total>=0.8 and 'boss' not in s['xp_events']:s['xp_events']['boss']=80 if b['mode']=='simulation' else 40
            return boss_view(id,b)|{'state':state_view(s)}
        if path=='/api/report':
            text=d.get('text','')
            if not isinstance(text,str) or not text.strip() or len(text)>2000:raise Invalid('Enter a short issue description.')
            s['feedback'].append({'text':text,'created':time.time(),'item':str(d.get('item',''))[:100]})
            return {'saved':True}
        raise Invalid('Unknown action.')


class AppServer(ThreadingHTTPServer):
    def server_close(self):
        if hasattr(self,'workflows'):self.workflows.close()
        super().server_close()


def make_server(port=8765,db=None,upload_directory=None,start_workers=True):
    DATA.mkdir(parents=True,exist_ok=True)
    DATA.chmod(0o700)
    server=AppServer(('127.0.0.1',port),Handler)
    server.store=Store(db or DATA/'progress.sqlite3')
    server.studio=Studio(server.store,upload_directory or DATA/'uploads')
    server.tutor=Tutor(server.store)
    server.tutor.studio=server.studio
    server.workflows=Workflows(server.store,server.studio,server.tutor.gateway,grade,directory=Path(server.store.file).parent/'work')
    server.tutor.workflows=server.workflows
    server.auth=Accounts(server.store)
    server.store.auth=server.auth
    if start_workers:server.workflows.start()
    return server


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765)
    server=make_server(parser.parse_args().port)
    print(f'Kinematics local demo: http://127.0.0.1:{server.server_port}',flush=True)
    if server.auth.setup_file.exists():print('Administrator setup is private. Run: python3 kinematics/account_setup.py',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
