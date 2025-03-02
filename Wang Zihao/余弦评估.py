
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ====================== 配置部分（需修改） ======================
INPUT_CSV = r"C:\Users\Wang Zihao\Desktop\QA_with_answers.csv"  # 确保文件路径正确
OUTPUT_CSV = r"C:\Users\Wang Zihao\Desktop\final_scores.csv"    #  自定义输出路径
# ==============================================================

def main():
    try:
        # 加载模型
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 读取CSV（保持您的编码设置）
        df = pd.read_csv(INPUT_CSV, encoding='Windows-1252')  # 保留您指定的编码
        
        # 🔄 修改点1：更新列名检查
        required_columns = ['text_answer', 'answer_qwen']  # 原reference_answer→text_answer
        if not set(required_columns).issubset(df.columns):
            missing = set(required_columns) - set(df.columns)
            raise ValueError(f"CSV文件缺少必要列: {missing}")

        # 生成文本向量
        print(" 正在编码参考答案...")
        embeddings = {
            'text': model.encode(df['text_answer'], show_progress_bar=True),  # 🔄 修改点2
            'qwen': model.encode(df['answer_qwen'], show_progress_bar=True)
        }

        # 计算相似度
        print("正在计算余弦相似度...")
        df['sim_qwen'] = cosine_similarity(
            embeddings['text'],   # 🔄 修改点3
            embeddings['qwen']
        ).diagonal()

        # 数值修正
        epsilon = 1e-8
        df['sim_qwen'] = np.clip(df['sim_qwen'], -1.0+epsilon, 1.0-epsilon).round(4)

        # 保存结果
        df.to_csv(OUTPUT_CSV, index=False, encoding='Windows-1252')
        print(f"""
        ✅ 评估完成！
        - 有效样本数: {len(df)} 条
        - 相似度分布: 
          平均 {df['sim_qwen'].mean():.4f} 
          标准差 ±{df['sim_qwen'].std():.2f}
          区间 [{df['sim_qwen'].min():.4f}, {df['sim_qwen'].max():.4f}]
        📂 文件已保存至: {OUTPUT_CSV}
        """)

    except FileNotFoundError:
        print(f"文件未找到，请检查路径: {INPUT_CSV}")
    except pd.errors.EmptyDataError:
        print(f"文件内容为空: {INPUT_CSV}")
    except Exception as e:
        print(f"运行异常: {str(e)}")

if __name__ == "__main__":
    main()