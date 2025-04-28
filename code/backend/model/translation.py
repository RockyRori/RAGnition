import asyncio
from typing import Literal, Union

from googletrans import Translator


async def async_translate(text: Union[str, list[str]], target_language: Literal['en', 'zh-cn', 'zh-tw'] = 'en'):
    translator = Translator()
    try:
        translation = await translator.translate(text, dest=target_language)
        if isinstance(text, str):
            return translation.text
        elif isinstance(text, list):
            return [t.text for t in translation]
    except Exception as e:
        print("翻译出错:", e)
        return text


def sync_translate(text, target_language: Literal['en', 'zh-cn', 'zh-tw'] = 'en'):
    # 使用 asyncio.run 在同步环境中运行异步函数
    return asyncio.run(async_translate(text, target_language))


if __name__ == "__main__":
    original_text = ""
    translated_text = ""
    original_list = ""
    translated_list = ""
    print("original_text", original_text)
    print("translated_text", translated_text)
    print("original_list", original_list)
    print("translated_list", translated_list)
