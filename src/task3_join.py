"""主动请求加入：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '看起来真有趣呀！如果你也想玩，可以试着告诉他们哦！'

TASK_RULES = '''
目标是向当前同伴表达一起活动或加入的意愿。"我可以和你们一起玩吗"、"我也想搭积木"、"可以加我一个吗"、"我想和你们一起玩"、"一起玩吧"为 yes。不要求固定句式或一定使用问句。"我喜欢积木"仅表达兴趣，"你好"仅表达问候，单独的"想"或"好"若本轮提示没有清楚询问加入意愿，则为 unclear；本轮明确询问是否想一起玩时，可接受清楚的简短肯定回答。"不想玩"、"我不想加入"为 no。不能把问候等同于加入请求。
'''


def evaluate_join_request(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_join_request, TASK_PROMPT)
