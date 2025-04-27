import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

POLICIES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base", "default", "policies")
PIECES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base", "default", "pieces")


def locate_path(*subdirs):
    """
    按需拼接 PROJECT_ROOT 下的任意子目录。
    例： locate_path('knowledge_base', 'default','pieces') → PIECES_DIR
    """
    return os.path.join(PROJECT_ROOT, *subdirs)
