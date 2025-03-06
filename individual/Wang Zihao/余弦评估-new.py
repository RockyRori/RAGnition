import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

# ====================== 配置部分（需修改） ======================
INPUT_CSV = r"C:\Users\Wang Zihao\Desktop\QA_with_answers.csv"  #!!!!! 输入文件路径
OUTPUT_CSV = r"C:\Users\Wang Zihao\Desktop\final_scores.csv"    #!!!!! 输出文件路径
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'            #!!!!! 可更换其他嵌入模型
# ==============================================================

class CosineEvaluator:
    """余弦相似度评估器"""
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载数据并校验格式"""
        try:
            df = pd.read_csv(file_path, encoding='Windows-1252')  #!!!!! 保持原编码
            required_cols = ['text_answer', 'answer_qwen']       #!!!!! 列名对应数据集
            missing = set(required_cols) - set(df.columns)
            if missing:
                raise ValueError(f"CSV缺少必要列: {missing}")
            return df
        except Exception as e:
            logging.error(f"数据加载失败: {str(e)}")
            raise

    def calculate_similarity(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算相似度并返回结果"""
        try:
            # 生成嵌入向量
            embeddings = {
                'ref': self.model.encode(df['text_answer'], show_progress_bar=True),
                'gen': self.model.encode(df['answer_qwen'], show_progress_bar=True)
            }
            
            # 计算相似度
            sim_scores = cosine_similarity(embeddings['ref'], embeddings['gen']).diagonal()
            df['sim_qwen'] = np.clip(sim_scores, -1.0+1e-8, 1.0-1e-8).round(4)
            return df
        except Exception as e:
            logging.error(f"相似度计算失败: {str(e)}")
            raise

def main():
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    
    try:
        evaluator = CosineEvaluator()
        
        # 加载数据
        logging.info("正在加载数据...")
        df = evaluator.load_data(INPUT_CSV)
        
        # 计算相似度
        logging.info("正在计算余弦相似度...")
        df = evaluator.calculate_similarity(df)
        
        # 保存结果
        df.to_csv(OUTPUT_CSV, index=False, encoding='Windows-1252')
        logging.info(f"""
        ✅ 评估完成！
        样本数量: {len(df)} 条
        平均相似度: {df['sim_qwen'].mean():.4f} 
        标准差: ±{df['sim_qwen'].std():.2f}
        结果文件: {OUTPUT_CSV}
        """)
        
    except Exception as e:
        logging.error(f"程序异常终止: {str(e)}")

if __name__ == "__main__":
    main()