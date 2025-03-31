import os
from dashscope import Generation
import dashscope
from dotenv import load_dotenv
import asyncio
import concurrent.futures

load_dotenv()


class StreamQwenPlusClient:
    def __init__(self):
        dashscope.api_key = os.getenv('tongyiqianwen')

    def ask(self, prompt):
        responses = Generation.call(
            model='qwen-plus',
            prompt=prompt,
            stream=True,  # 流式调用
            top_p=0.8,
            temperature=0.9
        )
        # 将响应逐条 yield 出来
        for response in responses:
            if response.output and response.output.text:
                yield response.output.text


stream_qwen_plus_client = StreamQwenPlusClient()


async def stream_qwen_plus_query(prompt: str):
    """
    异步生成器：通过线程池将同步生成器包装为异步生成器，
    每当有新 token 产生时，通过 asyncio.Queue 通知异步循环 yield token。
    """
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()

    def sync_producer():
        try:
            for token in stream_qwen_plus_client.ask(prompt):
                # 将 token 放入队列（注意这里使用 run_coroutine_threadsafe）
                asyncio.run_coroutine_threadsafe(q.put(token), loop)
        finally:
            # 完成后向队列放入 None 表示结束
            asyncio.run_coroutine_threadsafe(q.put(None), loop)

    # 使用线程池来执行同步的生成器
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    executor.submit(sync_producer)

    # 异步循环，从队列中逐个 yield token
    while True:
        token = await q.get()
        if token is None:
            break
        yield token


# 测试入口
if __name__ == "__main__":
    async def main():
        async for token in stream_qwen_plus_query("水浒传是谁写的？只回答名字。"):
            print(token, end='', flush=True)
        print()  # 换行美化输出


    asyncio.run(main())
