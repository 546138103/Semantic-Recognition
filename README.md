# Semantic Recognition

面向儿童社交互动游戏的文本语义判断实验，使用火山方舟 API，输出结构化的 `yes`、`no` 或 `unclear` 判断及原因。

## 文件说明

- `src/task_common.py`：公共 API 调用、结构化结果与终端入口。
- `src/task1.py`、`src/task2.py`：自我介绍与打招呼。
- `src/task3_willingness.py`、`src/task3_join.py`：参与意愿与加入请求。
- `src/task4_concern.py`、`src/task4_thanks.py`：关心同伴与回应感谢。
- `src/test_text_tasks.py`：不调用真实 API 的自动化测试。
- `json_schema_model.py`：结构化输出实验。
- `test_api.py`：检查环境变量是否存在，不打印密钥。
- `test_api_offcial`：Ark SDK 调用示例，文件名沿用现有名称。
- 根目录 Word 和 Markdown 文件：游戏设计及语音交互判断规则。

## 环境与运行

本机已验证 Python 3.14.0。当前直接依赖版本记录在 `requirements.txt`；API 模型默认值见各脚本，主任务可通过 `ARK_MODEL` 覆盖。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:ARK_API_KEY = '<your-api-key>'
.\.venv\Scripts\python.exe -B src\task1.py
```

运行后输入回答文本。测试 API 示例及非空文本的实际判断会发送 API 请求；下列自动化测试使用模拟客户端，不发送真实请求：

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s src -p 'test_*.py' -v
```

## Git 忽略规则

虚拟环境、缓存、密钥文件、日志、生成输出、本地模型和数据集不上传。`data/`、`datasets/`、`outputs/`、`results/` 等规则预留给后续本地数据与生成结果；现有源码、测试与设计文档正常纳入版本管理。

环境变量由脚本直接读取，当前代码没有自动加载 `.env` 的逻辑。请勿将真实 API Key 写入源码或提交到仓库。

初始化验证：现有 7 项自动化测试通过；没有在此次仓库整理中修改任务判断代码或调用真实 API。
