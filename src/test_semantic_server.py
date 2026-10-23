import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from semantic_server import create_app, validate_binding
from task_common import TaskResult

class ServerTests(unittest.TestCase):
    def test_task_receives_original_text_and_default_prompt(self):
        def evaluate(answer, prompt):
            return TaskResult(result='yes', reason='表达参与意愿', evidence=answer,
                              system_prompt=prompt, model='fixture')
        client = TestClient(create_app(evaluator=evaluate, service_token='test-token'))
        response = client.post('/v1/tasks/willingness', headers={'Authorization': 'Bearer test-token'},
                               json={'child_answer': ' 好呀\n我想玩 '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': 'yes', 'reason': '表达参与意愿',
                         'evidence': ' 好呀\n我想玩 ', 'system_prompt': '你想和他们一起玩吗？', 'model': 'fixture'})

    def test_unauthorized_request_never_calls_evaluator(self):
        def forbidden(*args): self.fail('未经授权不得调用模型')
        client=TestClient(create_app(evaluator=forbidden, service_token='test-token'))
        self.assertEqual(client.post('/v1/tasks/willingness', json={'child_answer':'想'}).status_code,401)

    def test_upstream_failure_hides_exception_and_is_not_child_failure(self):
        def broken(*args): raise RuntimeError('private-api-key-or-upstream-detail')
        client=TestClient(create_app(evaluator=broken, service_token='test-token'))
        r=client.post('/v1/tasks/willingness',json={'child_answer':'想'},headers={'Authorization':'Bearer test-token'})
        self.assertEqual(r.status_code,502)
        self.assertNotIn('private',r.text)
        self.assertNotIn('result',r.json())

    def test_invalid_body_does_not_call_evaluator(self):
        def forbidden(*args): self.fail('无效请求不得调用模型')
        client=TestClient(create_app(evaluator=forbidden, service_token='test-token'))
        for body in ({'child_answer':123},{'child_answer':'想','api_key':'bad'}, {'child_answer':'想','system_prompt':'  '}):
            self.assertEqual(client.post('/v1/tasks/willingness',json=body,headers={'Authorization':'Bearer test-token'}).status_code,422)

    def test_missing_server_key_returns_service_error(self):
        with patch.dict('os.environ',{'ARK_API_KEY':''}):
            client=TestClient(create_app(service_token='test-token'))
            r=client.post('/v1/tasks/willingness',json={'child_answer':'想'},headers={'Authorization':'Bearer test-token'})
            self.assertEqual(r.status_code,503)

    def test_public_binding_requires_service_token(self):
        with self.assertRaises(ValueError): validate_binding('0.0.0.0','')
        validate_binding('127.0.0.1','')
        validate_binding('0.0.0.0','test-token')

if __name__ == '__main__': unittest.main()
