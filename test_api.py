import os

print("Python 环境正常！")
print("API Key 是否存在：", bool(os.getenv("ARK_API_KEY")))