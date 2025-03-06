import csv
from datetime import datetime
from typing import List, Dict

# ====================== 配置部分（需修改） ======================
RATING_FILE = r"C:\Users\Wang Zihao\Desktop\user_ratings.csv"  #!!!!! 评分记录文件路径
# ==============================================================

class RatingSystem:
    """用户评分管理系统"""
    def __init__(self):
        self.fields = ['timestamp', 'question', 'answer', 'rating']  #!!!!! 可添加更多字段
        
    def save_rating(self, question: str, answer: str, rating: int) -> None:
        """保存用户评分"""
        try:
            with open(RATING_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                if f.tell() == 0:  # 新文件时写入表头
                    writer.writeheader()
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'question': question,
                    'answer': answer,
                    'rating': rating
                })
        except Exception as e:
            logging.error(f"评分保存失败: {str(e)}")

    def load_ratings(self) -> List[Dict]:
        """加载历史评分数据"""
        try:
            with open(RATING_FILE, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            return []