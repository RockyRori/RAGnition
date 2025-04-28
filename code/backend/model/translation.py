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


if __name__ == "__main__":
    original_text = "我是岭南大学政策小助手"
    translated_text = asyncio.run(async_translate(original_text, "zh-tw"))
    original_list = ["how about running", "請根據用戶問題和參考資料來回答"]
    translated_list = asyncio.run(async_translate(original_list, "zh-cn"))
    print("original_text", original_text)
    print("translated_text", translated_text)
    print("original_list", original_list)
    print("translated_list", translated_list)
