import re
import argparse
from typing import List


class TextSegmenter:
    def __init__(self, custom_pattern: str = None):
        self.default_pattern = r'''[,./;'`\[\]<>?:"{}~？!@#$%^&*()\-=_+\|，。、；‘’【】·！…（）\s]'''
        self.pattern = custom_pattern or self.default_pattern

    def segment(self, text: str) -> List[str]: #文本切割核心方法
        try:
            segments = [s.strip() for s in re.split(self.pattern, text) if s.strip()]
            return self._merge_short_segments(segments)
        except Exception as e:
            raise RuntimeError(f"分割失败: {str(e)}")

    def _merge_short_segments(self, segments: List[str], threshold: int = 30) -> List[str]:#合并过短文本块
        merged = []
        buffer = ""

        for seg in segments:
            if len(buffer) + len(seg) <= threshold:
                buffer += " " + seg if buffer else seg
            else:
                if buffer:
                    merged.append(buffer)
                buffer = seg

        if buffer:
            merged.append(buffer)

        return merged


def main():
    parser = argparse.ArgumentParser(
        description="文本分割处理器 v1.0",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-i', '--input', type=str,
                        help='输入文件路径')
    parser.add_argument('-o', '--output', type=str,
                        help='输出文件路径')
    parser.add_argument('-t', '--threshold', type=int, default=30,
                        help='合并阈值')

    args = parser.parse_args()

    segmenter = TextSegmenter()

    try:
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            print("请输入待处理的文本（Ctrl+Z 回车结束输入）：")
            content = '\n'.join(iter(input, ''))

        if not content.strip():
            raise ValueError("输入内容不能为空")

        # 执行分割处理
        segments = segmenter.segment(content)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(segments))
            print(f"\n✅ 成功处理并保存到 {args.output}")
        else:
            print("\n📝 分割结果：")
            for idx, seg in enumerate(segments, 1):
                print(f"{idx:02d}. {seg}")

        print(f"\n总计分割为 {len(segments)} 个段落")

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()