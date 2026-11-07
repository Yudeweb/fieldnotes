"""End-to-end agent workflows with no external model or resource requests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kinematics'))
from ai import Tutor, AIError
from agents import Workflows,WorkflowError,digest
from gateway import validate
from resources import public_target, ResourceError
from server import Store,grade
from studio import Studio


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        directory=Path(self.tmp.name);self.store=Store(directory/'app.sqlite');self.studio=Studio(self.store,directory/'uploads')
        self.config={'key':'fake-key-never-sent','enabled':False,'model':'gpt-6-luna','session_cap':.1,'day_cap':.25,'month_cap':2}
        self.calls=[]
        def forbidden(*args):self.calls.append(args);raise AssertionError('A paid call was attempted in offline mode')
        self.tutor=Tutor(self.store,lambda:self.config,forbidden,evidence=[])
        self.service=Workflows(self.store,self.studio,self.tutor.gateway,grade,directory/'work',extractor=self.extract,fetcher=lambda url:{'url':url,'title':'Public kinematics resource','excerpt':'Velocity and acceleration in circular motion.'})
        self.owner='reviewer';self.student='learner';self.service.claim(self.owner)
        self.course=self.studio.create(self.owner,{'title':'Physics I','code':'PHY','language':'English'})['id']
        self.doc=self.studio.upload(self.owner,self.course,'theory.pdf','lecture',False,b'%PDF-1.4\nlocal fixture')
        self.task_index=0

    def extract(self,file,render=None,student=False):
        return {'pages':[{'page':1,'text':'Position, displacement and velocity are measured in a reference frame.','low_text':False},{'page':2,'text':'Restricted answer: 999 units.','low_text':False}], 'images':[{'page':render or 1,'data':'data:image/jpeg;base64,/9j/'}] if render or student else []}

    def task(self,role,data=None,course=''):
        self.task_index+=1;payload={'id':f'workflow-test-task-{self.task_index:04d}',**(data or {})}
        job=self.service.queue(self.owner,role,payload,course);self.assertTrue(self.service.run_next());job=self.service.job(self.owner,job['id'])
        self.assertEqual(job['status'],'complete',job['error']);return job['result']

    def confirmed_source(self):
        record=self.task('source_reader',{'document':self.doc['id']},self.course)
        return self.service.confirm_source(self.owner,record['id'],{'revision':record['revision'],'pages':[{'page':1,'text':record['payload']['pages'][0]['text'],'classification':'theory','answer_free':True},{'page':2,'text':'Restricted answer: 999 units.','classification':'solutions','answer_free':False}]})

    def publish_pack(self):
        source=self.confirmed_source();structure=self.task('builder_structure',course=self.course)
        structure=self.service.review(self.owner,structure['id'],{'revision':structure['revision'],'action':'approve','confirmed':True})
        content=self.task('builder_content',{'structure':structure['id'],'unit':'describe'},self.course)
        content=self.service.review(self.owner,content['id'],{'revision':content['revision'],'action':'approve','confirmed':True})
        pack=self.service.publish(self.owner,content['id'],{'revision':content['revision'],'confirmed':True})
        return source,structure,content,pack

    def test_offline_source_builder_review_publish_and_invalidation(self):
        source,structure,content,pack=self.publish_pack()
        self.assertEqual(self.calls,[])
        self.assertEqual(pack['execution'],'offline')
        self.assertEqual(len(self.service.packs()),1)
        text=json.dumps(pack)
        self.assertNotIn('reference_solution',text);self.assertNotIn('999',text);self.assertNotIn('rubric',text)
        private=self.service.published(pack['id'],private=True)
        self.assertIn('reference_solution',private['payload']['units'][0]['checkpoint'])
        self.assertEqual(self.service.publish(self.owner,content['id'],{'revision':content['revision'],'confirmed':True})['id'],pack['id'])
        with self.assertRaises(WorkflowError):self.service.published_source(pack['id'],source['id'],2)
        self.assertIn('image',self.service.published_source(pack['id'],source['id'],1))
        self.studio.classify(self.owner,self.course,self.doc['id'],{'kind':'solution','contains_solutions':True})
        self.assertEqual(self.service.packs(),[])
        with self.assertRaises(WorkflowError):self.service.published(pack['id'])

    def test_no_automatic_release_or_structure_approval(self):
        record=self.task('source_reader',{'document':self.doc['id']},self.course)
        self.assertEqual(self.service.source_evidence(self.owner,self.course),[])
        with self.assertRaises(WorkflowError):self.service.confirm_source(self.student,record['id'],{})
        source=self.service.confirm_source(self.owner,record['id'],{'revision':1,'pages':[{'page':1,'text':'A theory page','classification':'theory','answer_free':False}]})
        self.assertEqual([e for e in self.service.source_evidence(self.owner,self.course) if e['authority']=='official'],[])
        with self.assertRaises(WorkflowError):self.service.publish(self.owner,source['id'],{'revision':source['revision'],'confirmed':True})
        self.assertEqual(self.calls,[])

    def test_wrong_transcription_preserved_locked_then_evaluated(self):
        work=self.service.typed_work(self.student,{'question':'cp1','text':'distance = 3 + 4 = 8; displacement = 5 m'})
        job=self.service.queue(self.student,'student_reader',{'id':'student-reader-job-0001','work':work['id']});self.service.run_next();work=self.service.job(self.student,job['id'])['result']
        self.assertIn('3 + 4 = 8',work['payload']['transcription'])
        with self.assertRaises(WorkflowError):self.service.confirm_work(self.student,work['id'],{'revision':work['revision'],'text':'x','checked_uncertainties':False})
        work=self.service.confirm_work(self.student,work['id'],{'revision':work['revision'],'text':work['payload']['transcription'],'answers':{'distance':8,'displacement':5,'speed':1.4},'checked_uncertainties':True})
        with self.assertRaises(WorkflowError):self.service.confirm_work(self.student,work['id'],{'revision':work['revision'],'text':'Different work','checked_uncertainties':True})
        q=self.service.rubrics(self.owner)[0]
        self.service.approve_rubric(self.owner,{'question':q['question'],'question_hash':q['question_hash'],'criteria':['Check the reasoning and units.'],'confirmed':True})
        job=self.service.queue(self.student,'evaluator',{'id':'student-evaluator-job-0001','work':work['id']});self.service.run_next();result=self.service.job(self.student,job['id'])
        self.assertEqual(result['status'],'complete',result['error']);feedback=result['result']['payload']
        self.assertEqual(feedback['numeric']['correct'],2);self.assertTrue(feedback['review_required']);self.assertEqual(feedback['meta']['cost_usd'],0)
        self.assertEqual(self.store.load(self.student)['xp_events'],{})
        self.assertEqual(self.calls,[])
        with self.assertRaises(WorkflowError):self.service.record(self.owner,work['id'])
        dispute=self.service.dispute(self.student,result['result']['id'],{'share_with_reviewer':True,'reason':'Please check my addition.'})
        self.assertTrue(dispute['payload']['consent']);self.assertIn('3 + 4 = 8',dispute['payload']['transcription'])

    def test_reader_live_payload_has_no_reference_answers(self):
        self.config['enabled']=True
        def fake(key,body):
            self.calls.append(body);return {'status':'completed','usage':{'input_tokens':10,'output_tokens':10},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'text':'3 + 4 = 8','uncertainties':['Check handwritten 8.'],'diagram_notes':[]})}]}]}
        self.tutor.gateway.transport=fake
        work=self.service.typed_work(self.student,{'question':'cp1','text':'3 + 4 = 8'})
        job=self.service.queue(self.student,'student_reader',{'id':'reader-live-mocked-0001','work':work['id']});self.service.run_next()
        self.assertEqual(self.service.job(self.student,job['id'])['status'],'complete')
        payload=json.loads(self.calls[0]['input']);self.assertNotIn('reference',json.dumps(payload));self.assertNotIn('solution',json.dumps(payload))
        self.assertEqual(payload['native_text'],'3 + 4 = 8')

    def test_curator_threshold_and_no_private_context(self):
        empty=self.task('curator');self.assertEqual(empty['status'],'insufficient_data');self.assertEqual(self.calls,[])
        for n in range(5):
            owner=f'session-{n}'
            def update(s):s['checks']['cp1']={'correct':0,'total':3};s['notes']='PRIVATE NOTE SENTINEL'
            self.store.update(owner,update);self.service.signals(owner,{'question':'cp1','category':'unclear_wording'})
        result=self.task('curator');serialized=json.dumps(result['payload'])
        self.assertNotIn('PRIVATE NOTE',serialized);self.assertNotIn('session-',serialized)
        self.assertEqual(result['payload']['aggregate']['groups'][0]['attempted_sessions'],5)
        self.assertTrue(result['payload']['clarifications'])
        self.service.review(self.owner,result['id'],{'revision':result['revision'],'action':'approve','confirmed':True})
        shared=self.service.shared_evidence('motion');self.assertTrue(any(e['authority']=='collective' for e in shared))
        self.assertEqual(self.calls,[])

    def test_scout_requires_review_and_votes_are_idempotent(self):
        record=self.task('scout',{'url':'https://example.org/kinematics','concept':'describe'})
        self.assertEqual(self.service.public_resources(),[])
        self.service.review(self.owner,record['id'],{'revision':record['revision'],'action':'approve','confirmed':True})
        self.assertEqual(self.service.public_resources()[0]['authority'],'Reviewed supplementary resource')
        self.service.vote(self.student,record['id']);self.service.vote(self.student,record['id'])
        self.assertIsNone(self.service.public_resources()[0]['helpful_sessions'])
        for n in range(4):self.service.vote('other-'+str(n),record['id'])
        self.assertEqual(self.service.public_resources()[0]['helpful_sessions'],5)
        self.assertEqual(self.calls,[])

    def test_other_session_cannot_claim_reviewer_or_read_jobs(self):
        with self.assertRaises(WorkflowError):self.service.claim(self.student)
        job=self.service.queue(self.owner,'curator',{'id':'private-job-test-0001'})
        with self.assertRaises(WorkflowError):self.service.job(self.student,job['id'])
        with self.assertRaises(WorkflowError):self.service.queue(self.student,'curator',{'id':'other-curator-job-0001'})

    def test_job_idempotency_and_execution_mode_bound_at_queue(self):
        job=self.service.queue(self.owner,'curator',{'id':'deduplicated-job-0001'})
        same=self.service.queue(self.owner,'curator',{'id':'deduplicated-job-0001'})
        self.assertEqual(job['id'],same['id']);self.assertEqual(len(self.service.jobs(self.owner)),1)
        self.config['enabled']=True
        for n in range(5):self.store.update('test-'+str(n),lambda s:s['checks'].update(cp1={'correct':0,'total':3}))
        self.service.run_next();result=self.service.job(self.owner,job['id'])
        self.assertEqual(result['status'],'complete');self.assertEqual(result['result']['payload']['meta']['execution'],'offline');self.assertEqual(self.calls,[])

    def test_all_agent_help_blocked_during_simulation(self):
        self.store.update(self.owner,lambda s:s['bosses'].update(attempt={'mode':'simulation','submitted':False}))
        for role in ('student_reader','evaluator','builder_structure','curator','scout','source_reader'):
            with self.assertRaises(WorkflowError):self.service.queue(self.owner,role,{'id':'blocked-task-'+role.replace('_','-')},self.course)
        self.assertEqual(self.calls,[])

    def test_source_classification_change_rejects_stale_confirmation(self):
        r=self.task('source_reader',{'document':self.doc['id']},self.course)
        self.studio.classify(self.owner,self.course,self.doc['id'],{'kind':'solution','contains_solutions':True})
        with self.assertRaises(WorkflowError):self.service.confirm_source(self.owner,r['id'],{'revision':1,'pages':[{'page':1,'text':'Theory','classification':'theory','answer_free':True}]})

    def test_schema_validation_rejects_extra_fields(self):
        from agents import TRANSCRIPT
        with self.assertRaises(ValueError):validate({'text':'hello','uncertainties':[],'diagram_notes':[],'grade':100},TRANSCRIPT)

    def test_study_time_suppression_and_explicit_reference_flag(self):
        for n in range(4):self.service.track_time('time-'+str(n),{'question':'cp1','seconds':20})
        self.assertEqual(self.service.aggregates()['study_time'],[])
        self.service.track_time('time-4',{'question':'cp1','seconds':20})
        self.assertEqual(self.service.aggregates()['study_time'],[{'question':'cp1','sessions':5,'median_seconds':20}])
        with self.assertRaises(WorkflowError):self.service.track_time(self.student,{'question':'cp1','seconds':5000})
        self.service.signals(self.student,{'question':'cp1','category':'wrong_reference'})
        self.service.signals(self.student,{'question':'cp1','category':'wrong_reference'})
        self.assertEqual(len(self.service.records(self.owner,'clarification')),1)

    def test_budget_is_shared_between_agent_roles(self):
        from agents import obj,S
        self.config['enabled']=True
        def fake(key,body):
            self.calls.append(body)
            return {'status':'completed','usage':{'input_tokens':100,'output_tokens':10},'output':[{'type':'message','content':[{'type':'output_text','text':'{"answer":"OK"}'}]}]}
        self.tutor.gateway.transport=fake
        schema=obj(answer=S)
        self.tutor.gateway.generate(self.owner,'shared-budget-first-0001','student_reader','Basic prompt',{'question':'Hello'},schema,lambda:{'answer':'offline'})
        self.config['session_cap']=.00002
        with self.assertRaises(AIError):self.tutor.gateway.generate(self.owner,'shared-budget-second-0001','scout','Basic prompt',{'question':'Hello'},schema,lambda:{'answer':'offline'})
        self.assertEqual(len(self.calls),1)

    def test_inflight_evaluation_cannot_publish_feedback_after_simulation_starts(self):
        work=self.service.typed_work(self.student,{'question':'cp1','text':'Distance is 7 m.'})
        work=self.service.confirm_work(self.student,work['id'],{'revision':1,'text':'Distance is 7 m.','answers':{'distance':7},'checked_uncertainties':True})
        q=self.service.rubrics(self.owner)[0]
        self.service.approve_rubric(self.owner,{'question':'cp1','question_hash':q['question_hash'],'criteria':['Check units.'],'confirmed':True})
        self.config['enabled']=True
        def interrupted(key,body):
            self.store.update(self.student,lambda s:s['bosses'].update(new={'mode':'simulation','submitted':False}))
            return {'status':'completed','usage':{'input_tokens':10,'output_tokens':10},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'overall':'review_required','feedback':[],'misconceptions':[],'review_required':True})}]}]}
        self.tutor.gateway.transport=interrupted
        job=self.service.queue(self.student,'evaluator',{'id':'inflight-evaluation-0001','work':work['id']});self.service.run_next()
        self.assertEqual(self.service.job(self.student,job['id'])['status'],'failed')
        self.assertEqual(self.service.records(self.student,'evaluation'),[])

    def test_resource_target_rejects_private_network_and_credentials(self):
        def resolver(host,port,**kwargs):return [(2,1,6,'',('127.0.0.1',443))]
        for url in ('https://example.org/test','http://example.org','https://user:pass@example.org','https://example.org:8443','https://169.254.169.254/latest'):
            with self.assertRaises(ResourceError):public_target(url,resolver)
        def mixed(host,port,**kwargs):return [(2,1,6,'',('8.8.8.8',443)),(2,1,6,'',('10.0.0.1',443))]
        with self.assertRaises(ResourceError):public_target('https://example.org',mixed)


if __name__=='__main__':unittest.main()
