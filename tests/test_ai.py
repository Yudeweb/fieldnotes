"""No paid provider calls: test the boundary, budgets, retrieval and private memory."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'kinematics'))
from ai import AIError, Tutor
from server import Store


class TutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'state.sqlite')
        self.calls=[]
        self.config={'key':'test-not-a-key','enabled':True,'model':'gpt-6-luna','session_cap':.10,'day_cap':.25,'month_cap':2}
        self.tutor=Tutor(self.store,lambda:self.config,self.provider,evidence=[{'key':'mar03:16','source':'mar03','page':16,'title':'Official lecture','text':'Instantaneous velocity is the derivative of position.'}])
        self.data={'id':'message-id-00000001','message':'Explain velocity','language':'Italian','context':{'page':'level','section':'learn','lesson':'describe','checkpoint':'cp1'}}

    def provider(self,key,body):
        self.calls.append(body)
        return {'status':'completed','usage':{'input_tokens':1200,'output_tokens':100},'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'answer':'Velocity measures change in position.','citations':['mar03:16','secret-solutions:1']})}]}]}

    def ask(self,owner='student-a',data=None):
        return self.tutor.ask(owner,data or self.data,self.store.load(owner))

    def test_private_memory_idempotency_and_citation_allowlist(self):
        a=self.ask();b=self.ask()
        self.assertEqual(len(self.calls),1);self.assertEqual(a,b)
        self.assertEqual(a['citations'],[{'source':'mar03','page':16,'title':'Official lecture'}])
        self.assertEqual(self.tutor.history('student-b'),[])
        self.assertEqual(len(self.tutor.history('student-a')),1)
        prompt=json.loads(self.calls[0]['input'])
        self.assertEqual(prompt['explanation_language'],'Italian')
        self.assertNotIn('solution',json.dumps(prompt))
        self.assertNotIn('notes',prompt['page_context'])
        self.assertFalse(self.calls[0]['store'])
        self.assertEqual(self.calls[0]['max_output_tokens'],1800)
        self.assertEqual(self.calls[0]['reasoning'],{'effort':'low'})

    def test_reasoning_configuration_is_validated_and_bound_to_run_id(self):
        self.config['reasoning_effort']='unsupported'
        with self.assertRaises(AIError):self.ask()
        self.assertEqual(self.calls,[])
        self.config['reasoning_effort']='low';self.ask()
        self.config['reasoning_effort']='medium'
        with self.assertRaises(AIError):self.ask()
        self.assertEqual(len(self.calls),1)
        self.ask(data=self.data|{'id':'message-id-medium-0002'})
        self.assertEqual(self.calls[-1]['reasoning'],{'effort':'medium'})

    def test_changed_message_cannot_reuse_id(self):
        self.ask()
        with self.assertRaises(AIError):self.ask(data=self.data|{'message':'Different question'})
        self.assertEqual(len(self.calls),1)

    def test_session_and_global_budgets_stop_before_dispatch(self):
        self.config['session_cap']=0
        with self.assertRaises(AIError):self.ask()
        self.assertEqual(self.calls,[])
        self.config['session_cap']=.1;self.ask()
        self.config['day_cap']=.000001
        with self.assertRaises(AIError):self.ask('student-b')
        self.assertEqual(len(self.calls),1)

    def test_failures_not_retried_and_reservation_retained(self):
        def failure(key,body):self.calls.append(body);raise TimeoutError()
        self.tutor.transport=failure
        with self.assertRaises(AIError):self.ask()
        with self.assertRaises(AIError):self.ask()
        self.assertEqual(len(self.calls),1)
        self.assertGreater(self.tutor.status('student-a')['spent_usd'],0)

    def test_simulation_cannot_be_bypassed_through_course_page(self):
        state=self.store.load('student-a')
        state['bosses']['attempt']={'mode':'simulation','submitted':False,'deadline':1}
        result=self.tutor.ask('student-a',self.data|{'context':{'page':'course'}},state)
        self.assertTrue(result['blocked']);self.assertEqual(self.calls,[])

    def test_unknown_models_and_context_rejected_before_dispatch(self):
        with self.assertRaises(AIError):self.ask(data=self.data|{'context':{'page':'level','lesson':'secret'}})
        self.config['model']='unpriced-model'
        with self.assertRaises(AIError):self.ask()
        self.assertEqual(self.calls,[])

    def test_short_transactions_allow_state_writes_during_provider_call(self):
        provider=self.tutor.transport
        def writing(key,body):
            self.store.update('student-a',lambda s:s.update(notes='Concurrent saved note'))
            return provider(key,body)
        self.tutor.transport=writing
        self.ask();self.assertEqual(self.store.load('student-a')['notes'],'Concurrent saved note')


if __name__=='__main__':unittest.main()
