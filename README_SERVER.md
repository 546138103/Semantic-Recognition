# 参与意愿 HTTP 服务

先启动本项目的 `start_semantic_server.cmd`，再启动 ASR_Test 的 `start_asr_semantic.cmd`。

## 服务器启动

双击 `start_semantic_server.cmd`。如果没有进程环境变量 `ARK_API_KEY`，在服务器终端输入方舟 API Key，输入隐藏，仅保留在当前进程内。关闭服务器后不会保存密钥。

也可以在本项目 PowerShell 中配置并运行：

```powershell
$env:ARK_API_KEY = '<your-api-key>'
.\.venv\Scripts\python.exe -B -u semantic_server.py
```

默认监听 `127.0.0.1:8765`，只供本机联调。没有真实密钥、只检查 HTTP 接口时：

```powershell
.\.venv\Scripts\python.exe -B -u semantic_server.py --no-key-prompt
```

此模式不会模拟模型结果，非空回答会返回 HTTP 503；空回答沿用原逻辑返回 `unclear`，不调用上游。访问 `http://127.0.0.1:8765/health` 可检查服务状态和是否配置密钥，不返回密钥内容。

## 接口

`POST /v1/tasks/willingness` 接收 JSON：

```json
{"child_answer":"我想一起玩","system_prompt":"你想和他们一起玩吗？"}
```

`child_answer` 必填，`system_prompt` 可省略，默认为服务器任务提示；两者最多各 4096 字，提示不能是空白，拒绝额外字段，正文上限 64 KiB。服务器固定调用 `src/task3_willingness.py` 的 `evaluate_willingness`，规则和模型设置仍由服务器管理。

成功返回现有 `TaskResult`；失败使用 HTTP 状态，不伪造孩子判断：401/403 鉴权失败、413 正文过大、422 参数错误、429 服务器繁忙、502 上游模型调用失败、503 服务器未配密钥。最多同时处理 4 个语义调用。错误不回传上游异常原文；HTTP 访问日志关闭；终端显示收到的转写文字、本轮提示、语义结果、判断原因与耗时，程序不写入录音或结果日志文件。每次请求带短编号，便于对应接收和完成记录。

## 将来部署到独立服务器

设置 `ARK_API_KEY` 和独立的 `SEMANTIC_SERVICE_TOKEN`，再用 `--host 0.0.0.0` 启动。没有服务令牌时拒绝非本机监听。客户端通过 `Authorization: Bearer ...` 提供此令牌；令牌与方舟 Key 不同。

公网还需要配置 HTTPS 入口，客户端远程地址必须为 HTTPS。当前未配置公网域名、证书、正式用户登录或网关限流。请使用这里的启动脚本/semantic_server.py 入口，避免绕过启动配置检查。服务访问令牌用于当前原型接入控制，正式客户端发布时需要独立用户身份与额度管理。

`.env` 仍不会自动加载；环境变量需在服务器终端设置，或使用隐藏输入。不要把真实密钥写进代码、说明或 Git。

## 测试

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s src -p 'test_*.py' -v
```

自动测试不调用真实豆包 API。本机真实 HTTP 联调已验证客户端和现有空回答处理、鉴权失败、无密钥报错。要验证真实非空回答，请配置服务器 Key，再从 ASR 客户端使用 `--text "我想一起玩"`。

协议实现参考：[FastAPI 请求正文](https://fastapi.tiangolo.com/tutorial/body/)。
