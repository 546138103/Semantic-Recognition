"""主动打招呼：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '你已经走到新朋友身边啦！现在试着和他打个招呼吧！'

TASK_RULES = '''
目标是向当前同伴表达问候。"你好"、"嗨"、"哈喽"、"你们好"、"早上好"等自然问候为 yes，不要求附带姓名或"很高兴认识你"。问候中夹带其他话语也可为 yes，但若整体为否定、转述或讽刺而非实际问候，不可只按关键词判断。"我不想说你好"为 no；"老师让我说你好"为 unclear。仅说兴趣、姓名、加入意愿、"好"、"再见"、"讨厌你"而没有问候或明确拒绝打招呼，为 unclear。明确不愿打招呼为 no。
'''


def evaluate_greeting(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_greeting, TASK_PROMPT)
