import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "apply_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,  # 결과를 dict로 받기 위함
}


def get_connection():
    """요청마다 새 커넥션을 열고, 사용 후 반드시 close() 해야 함 (with문 권장)."""
    return pymysql.connect(**DB_CONFIG)
