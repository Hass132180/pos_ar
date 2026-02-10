"""
إدارة الاتصال بقاعدة البيانات
"""
import sqlite3
from contextlib import contextmanager
from config import DB_NAME


class DatabaseConnection:
    """مدير الاتصال بقاعدة البيانات"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.db_name = DB_NAME
    
    @contextmanager
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute(self, query, params=()):
        """تنفيذ استعلام"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query, params_list):
        """تنفيذ استعلامات متعددة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def fetch_one(self, query, params=()):
        """جلب صف واحد"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query, params=()):
        """جلب جميع الصفوف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()


# إنشاء مثيل واحد للاستخدام في جميع أنحاء التطبيق
db = DatabaseConnection()
