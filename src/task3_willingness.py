"""是否愿意参加：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '你想和他们一起玩吗？'

TASK_RULES = '''
目标是识别孩子是否愿意参加同伴的游戏。"想"、"好呀"、"我要玩"、"我想搭积木"等肯定参与意愿为 yes；"不想"、"不愿意"、"我想自己玩"等明确不参与为 no；沉默、"不知道"、仅描述玩具、无关回答或含义不清为 unclear。此处的 yes 只代表愿意参加，不能视为已经向同伴请求加入，也不能推断已经靠近或参加活动。
'''


def evaluate_willingness(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_willingness, TASK_PROMPT)
