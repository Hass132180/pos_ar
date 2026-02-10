"""
إدارة التحديثات وملء البيانات الأولية
"""
import hashlib
from database.connection import db
from database.models import DatabaseModels
from config import DEFAULT_ADMIN, DEFAULT_CATEGORIES
from utils.helpers import hash_password


class DatabaseMigrations:
    """إدارة تحديثات قاعدة البيانات"""
    
    @staticmethod
    def initialize():
        """تهيئة قاعدة البيانات"""
        try:
            print("🔧 جاري تهيئة قاعدة البيانات...")
            
            # إنشاء الجداول
            DatabaseModels.create_tables()
            
            # التأكد من وجود جدول المرتجعات (للقواعد القديمة)
            DatabaseMigrations.ensure_returns_table()
            
            print("✅ تمت تهيئة قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
            return False
    
    @staticmethod
    def ensure_returns_table():
        """التأكد من وجود جدول المرتجعات"""
        try:
            # فحص وجود الجدول
            table_exists = db.fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='returns'"
            )
            
            if not table_exists:
                print("🔧 إنشاء جدول المرتجعات...")
                db.execute("""
                    CREATE TABLE returns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sale_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        return_amount REAL NOT NULL,
                        user_id INTEGER NOT NULL,
                        reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (sale_id) REFERENCES sales (id),
                        FOREIGN KEY (product_id) REFERENCES products (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                print("✅ تم إنشاء جدول المرتجعات")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء جدول المرتجعات: {e}")
    
    @staticmethod
    def seed_default_data():
        """إضافة البيانات الافتراضية"""
        try:
            # إضافة المستخدم الافتراضي
            user_exists = db.fetch_one("SELECT COUNT(*) as count FROM users")
            if user_exists and user_exists['count'] == 0:
                password_hash = hashlib.sha256(
                    DEFAULT_ADMIN['password'].encode()
                ).hexdigest()
                
                db.execute(
                    """INSERT INTO users (username, password, full_name, role)
                       VALUES (?, ?, ?, ?)""",
                    (DEFAULT_ADMIN['username'], password_hash, 
                     DEFAULT_ADMIN['full_name'], DEFAULT_ADMIN['role'])
                )
                print("✅ تم إضافة المستخدم الافتراضي (المدير)")
                
                # إضافة مستخدم بائع للاختبار
                cashier_password = hash_password("cashier123")
                db.execute(
                    """INSERT INTO users (username, password, full_name, role)
                       VALUES (?, ?, ?, ?)""",
                    ("cashier", cashier_password, "بائع النظام", "cashier")
                )
                print("✅ تم إضافة مستخدم البائع (cashier/cashier123)")
            
            # إضافة الفئات الافتراضية
            categories_exist = db.fetch_one("SELECT COUNT(*) as count FROM categories")
            if categories_exist and categories_exist['count'] == 0:
                for category in DEFAULT_CATEGORIES:
                    db.execute(
                        "INSERT INTO categories (name) VALUES (?)",
                        (category,)
                    )
                print("✅ تم إضافة الفئات الافتراضية")
                
                # إضافة منتجات تجريبية
                category_id = db.fetch_one("SELECT id FROM categories WHERE name = 'قطع غيار'")['id']
                
                sample_products = [
                    ("فلتر زيت", 50.00, 30.00, 20, "001"),
                    ("فلتر هواء", 40.00, 25.00, 15, "002"),
                    ("شمعات", 80.00, 50.00, 30, "003"),
                    ("سير مروحة", 120.00, 80.00, 10, "004"),
                    ("بواجي", 100.00, 60.00, 25, "005"),
                ]
                
                for name, sell_price, cost_price, stock, barcode in sample_products:
                    db.execute(
                        """INSERT INTO products 
                           (name, category_id, sell_price, cost_price, stock, barcode)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (name, category_id, sell_price, cost_price, stock, barcode)
                    )
                
                print("✅ تم إضافة منتجات تجريبية")
            
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة البيانات: {e}")
            return False
