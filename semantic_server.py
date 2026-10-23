"""HTTP boundary for task3_willingness; ARK_API_KEY stays in this process."""
from __future__ import annotations
import argparse
import getpass
import hmac
import ipaddress
import os
from pathlib import Path
import sys
from threading import BoundedSemaphore
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from task3_willingness import TASK_PROMPT, evaluate_willingness
from task_common import TaskResult


def is_loopback(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host == 'localhost'


def validate_binding(host, token):
    if not is_loopback(host) and not token:
        raise ValueError('非本机监听必须设置 SEMANTIC_SERVICE_TOKEN；远程访问请通过 HTTPS。')


class WillingnessRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    child_answer: str = Field(max_length=4096)
    system_prompt: str = Field(default=TASK_PROMPT, max_length=4096)

    @field_validator('system_prompt')
    @classmethod
    def prompt_not_blank(cls, value):
        if not value.strip():
            raise ValueError('system_prompt 不能为空')
        return value


def create_app(*, evaluator=None, service_token=None):
    evaluate = evaluator or evaluate_willingness
    token = os.getenv('SEMANTIC_SERVICE_TOKEN', '') if service_token is None else service_token
    app = FastAPI(title='Willingness semantic service', docs_url=None, redoc_url=None)
    capacity = BoundedSemaphore(4)

    @app.middleware('http')
    async def limit_body(request: Request, call_next):
        # Streaming cap also handles requests without Content-Length.
        if request.method == 'POST':
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 65536:
                    return JSONResponse(status_code=413, content={'detail': '请求正文过大'})
            request._body = bytes(body)
        return await call_next(request)

    def authorize(request: Request, authorization: Annotated[str | None, Header()] = None):
        if token:
            expected = ('Bearer ' + token).encode('utf-8')
            actual = (authorization or '').encode('utf-8')
            if not hmac.compare_digest(actual, expected):
                raise HTTPException(status_code=401, detail='服务访问令牌无效')
        elif not request.client or not is_loopback(request.client.host):
            raise HTTPException(status_code=403, detail='未配置服务令牌，只允许本机访问')

    @app.get('/health')
    def health():
        return {'status': 'ok', 'task': 'willingness', 'api_configured': bool(os.getenv('ARK_API_KEY'))}

    @app.post('/v1/tasks/willingness', response_model=TaskResult, dependencies=[Depends(authorize)])
    def willingness(body: WillingnessRequest):
        if evaluator is None and body.child_answer.strip() and not os.getenv('ARK_API_KEY'):
            raise HTTPException(status_code=503, detail='服务器尚未配置 ARK_API_KEY')
        if not capacity.acquire(blocking=False):
            raise HTTPException(status_code=429, detail='服务器忙，请稍后重试')
        try:
            return evaluate(body.child_answer, body.system_prompt)
        except Exception:
            # Never relay upstream error bodies, keys or child text in error details.
            raise HTTPException(status_code=502, detail='语义模型调用失败，请检查服务器配置或稍后重试') from None
        finally:
            capacity.release()

    return app


def main():
    parser = argparse.ArgumentParser(description='语义识别服务器：API Key 只在这里配置')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-key-prompt', action='store_true', help='不询问密钥，供无密钥接口测试使用')
    args = parser.parse_args()
    token = os.getenv('SEMANTIC_SERVICE_TOKEN', '')
    try:
        validate_binding(args.host, token)
    except ValueError as error:
        parser.error(str(error))
    if not os.getenv('ARK_API_KEY') and not args.no_key_prompt:
        key = getpass.getpass('请在服务器输入 ARK_API_KEY（输入隐藏，不保存到文件）：').strip()
        if not key:
            parser.error('未输入 API Key；无密钥联调请使用 --no-key-prompt')
        os.environ['ARK_API_KEY'] = key
    import uvicorn
    print(f'语义服务：http://{args.host}:{args.port}；任务提示：{TASK_PROMPT}', flush=True)
    uvicorn.run(create_app(service_token=token), host=args.host, port=args.port,
                access_log=False, proxy_headers=False, limit_concurrency=16, timeout_keep_alive=5)


if __name__ == '__main__':
    main()
