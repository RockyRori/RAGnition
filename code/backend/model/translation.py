import asyncio
from googletrans import Translator


async def async_translate(text, target_language='en'):
    translator = Translator()
    try:
        translation = await translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print("翻译出错:", e)
        return text


def sync_translate(text, target_language='en'):
    # 使用 asyncio.run 在同步环境中运行异步函数
    return asyncio.run(async_translate(text, target_language))
