"""发现困难并表达关注或帮助意愿：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '哎呀！我的积木都掉到地上啦！这么多积木，我一个人捡好像有点困难……'

TASK_RULES = '''
情境是同伴遇到困难。目标是表达对同伴的关注或主动帮助意愿。"怎么啦"、"你怎么了"、"需要我帮忙吗"、"我来帮你"、"我帮你捡"为 yes；"积木掉了"仅描述现象，"你好"仅问候，未表达关注或帮助时为 unclear。明确表示不愿帮助或不愿关注为 no。yes 仅表示满足语言部分，不能推断孩子已靠近、拾取或放回积木。回应同伴请求由行动处理，本脚本不判断实际帮助完成。
'''


def evaluate_concern(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_concern, TASK_PROMPT)
