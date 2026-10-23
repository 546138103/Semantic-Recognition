"""回应同伴感谢：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '谢谢你帮助我！你真是一个友好的小伙伴！小朋友，你可以回应一下他哦！'

TASK_RULES = '''
情境是同伴刚刚向孩子表示感谢。目标是作出合适的口头回应。"不客气"、"没关系"、"不用谢"、"我们是朋友"等适当回应为 yes。本任务明确允许在感谢情境下单独回答"好"、"好的"、"嗯"，判 yes。无关回答、沉默或无法理解为 unclear。明确拒绝回应感谢为 no；辱骂而无适当回应或明确拒绝含义时为 unclear。不能推断点头、挥手等动作。
'''


def evaluate_thanks(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_thanks, TASK_PROMPT)
