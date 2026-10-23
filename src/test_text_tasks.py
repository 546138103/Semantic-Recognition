import importlib
import unittest
from unittest.mock import MagicMock, patch


TASKS = {
    'task1': 'evaluate_introduction',
    'task2': 'evaluate_greeting',
    'task3_willingness': 'evaluate_willingness',
    'task3_join': 'evaluate_join_request',
    'task4_concern': 'evaluate_concern',
    'task4_thanks': 'evaluate_thanks',
}


class TextTaskTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('task_common'), '缺少共用文本判定模块')
        self.common = importlib.import_module('task_common')

    def test_all_tasks_preserve_inputs_and_only_request_assessment(self):
        for module_name, function_name in TASKS.items():
            for decision in ('yes', 'no', 'unclear'):
                with self.subTest(task=module_name, decision=decision):
                    module = importlib.import_module(module_name)
                    client = MagicMock()
                    client.__enter__.return_value = client
                    client.responses.parse.return_value.output_parsed = self.common.Assessment(
                        result=decision, reason='模拟判定依据')
                    answer = ' 你好呀\n这是孩子的原话。 '
                    prompt = ' 人工设置的本轮提示 {保留大括号}\n '
                    with patch.object(self.common, 'OpenAI', return_value=client), patch.dict(
                        'os.environ', {'ARK_API_KEY': 'test-key', 'ARK_MODEL': 'test-model'}):
                        result = getattr(module, function_name)(answer, prompt)
                    self.assertEqual(result.model_dump(), dict(
                        result=decision, reason='模拟判定依据', evidence=answer, system_prompt=prompt, model='test-model'))
                    request = client.responses.parse.call_args.kwargs
                    self.assertEqual(result.model, request['model'])
                    self.assertEqual(set(request['text_format'].model_fields), {'result', 'reason'})
                    self.assertIn(__import__('json').dumps(prompt, ensure_ascii=False), request['input'][0]['content'])
                    self.assertIn(answer, __import__('json').loads(request['input'][1]['content'])['child_answer'])

    def test_empty_answer_does_not_call_api(self):
        for module_name, function_name in TASKS.items():
            with self.subTest(task=module_name):
                fn = getattr(importlib.import_module(module_name), function_name)
                with patch.object(self.common, 'OpenAI') as factory:
                    result = fn(' \n', '本轮提示')
                factory.assert_not_called()
                self.assertEqual(result.result, 'unclear')
                self.assertEqual(result.evidence, ' \n')

    def test_cli_only_asks_for_answer(self):
        evaluator = MagicMock()
        with patch('builtins.input', return_value='你好') as user_input, patch('builtins.print'):
            self.common.run_cli(evaluator, '默认提示')
        user_input.assert_called_once_with('请输入孩子的回答：')
        evaluator.assert_called_once_with('你好', '默认提示')

    def test_empty_answer_records_configured_model(self):
        with patch.dict('os.environ', {'ARK_MODEL': 'test-model'}):
            result = importlib.import_module('task2').evaluate_greeting('', '提示')
        self.assertEqual(result.model, 'test-model')
    def test_bad_inputs_fail_before_api(self):
        fn = importlib.import_module('task2').evaluate_greeting
        for args in ((None, '提示'), ('你好', None), ('你好', '  ')):
            with self.subTest(args=args), self.assertRaises((TypeError, ValueError)):
                fn(*args)

    def test_missing_key_missing_output_and_api_error_are_not_child_failure(self):
        fn = importlib.import_module('task2').evaluate_greeting
        with patch.dict('os.environ', {'ARK_API_KEY': ''}), self.assertRaises(RuntimeError):
            fn('你好', '提示')
        client = MagicMock()
        client.__enter__.return_value = client
        with patch.object(self.common, 'OpenAI', return_value=client), patch.dict(
            'os.environ', {'ARK_API_KEY': 'test-key', 'ARK_MODEL': 'test-model'}):
            client.responses.parse.return_value.output_parsed = None
            with self.assertRaises(RuntimeError):
                fn('你好', '提示')
            client.responses.parse.side_effect = TimeoutError('模拟超时')
            with self.assertRaises(TimeoutError):
                fn('你好', '提示')

    def test_schema_rejects_unexpected_fields_and_result(self):
        from pydantic import ValidationError
        for data in ({'result': 'other', 'reason': 'x'},
                     {'result': 'yes', 'reason': 'x', 'evidence': '模型不应返回原文'}):
            with self.assertRaises(ValidationError):
                self.common.Assessment(**data)


if __name__ == '__main__':
    unittest.main()