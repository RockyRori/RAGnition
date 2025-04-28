import os
import re
from PIL import Image
import pytesseract

# 如果 tesseract 不在 PATH，可在此处指定：
pytesseract.pytesseract.tesseract_cmd = r'C:\SoftWare\Tesseract-OCR\tesseract.exe'


def extract_text_from_images(folder_path: str, lang: str = 'chi_sim') -> str:
    """
    扫描 folder_path 目录下所有名为 “<prefix>_<number>.png” 的文件，
    按 <number> 升序提取文字并拼接成文章。
    """
    # 匹配后缀为 .png 且含“_数字”模式的文件
    pattern = re.compile(r'^(?P<prefix>.+)_(?P<num>\d+)\.png$', re.IGNORECASE)
    files = []
    for fname in os.listdir(folder_path):
        m = pattern.match(fname)
        if m:
            num = int(m.group('num'))
            files.append((num, fname))
    # 按数字排序
    files.sort(key=lambda x: x[0])

    paragraphs = []
    for num, fname in files:
        img_path = os.path.join(folder_path, fname)
        try:
            img = Image.open(img_path)
        except Exception as e:
            print(f"⚠️ 无法打开图片 {fname}：{e}")
            continue

        # OCR 提取（默认为简体中文，若需中英混合可改为 'chi_sim+eng'）
        text = pytesseract.image_to_string(img, lang=lang).strip()
        if text:
            paragraphs.append(f"【{fname}】\n{text}")

    # 段落间空行分隔
    return "\n\n".join(paragraphs)


if __name__ == "__main__":
    INPUT_FOLDER = "picture"  # 存放 PNG 的文件夹
    OUTPUT_FILE = "article.txt"  # 输出的文本文件

    article = extract_text_from_images(INPUT_FOLDER, lang='chi_sim+eng')
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"✅ 已将按编号拼接的 OCR 结果保存至：{OUTPUT_FILE}")
