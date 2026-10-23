"""自我介绍：传入本轮文本和人工提示，返回结构化结果。"""
from task_common import TaskResult, evaluate_text, run_cli

TASK_PROMPT = '你可以开始介绍自己啦！可以告诉大家你叫什么名字、今年几岁了，还有你喜欢玩什么！'

TASK_RULES = '''
目标是表达自己的具体个人信息。单轮回答中，姓名、年龄、具体兴趣爱好、个人经历或其他明确描述自身的具体信息，任一项即可判 yes；不要求同时包含姓名、年龄和爱好，不累计多轮、不核验身份真伪。"我叫小明"、"我五岁"、"我喜欢画画"、"我上幼儿园"均为 yes。结合本轮明确问题，"小明"、"五岁"、"搭积木"等简短回答也可为 yes；无法确定是否在介绍自己时为 unclear。只有"你好"、"我"、"不知道"、"我喜欢玩"等缺乏具体个人信息的表达为 unclear。明确拒绝介绍自己为 no。
'''


def evaluate_introduction(child_answer: str, system_prompt: str) -> TaskResult:
    return evaluate_text(child_answer, system_prompt, TASK_RULES)


if __name__ == '__main__':
    run_cli(evaluate_introduction, TASK_PROMPT)
