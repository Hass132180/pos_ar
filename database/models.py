"""
نماذج قاعدة البيانات - تعريف الجداول
"""
from database.connection import db


class DatabaseModels:
    """نماذج قاعدة البيانات"""
    
    @staticmethod
    def create_tables():
        """إنشاء جداول قاعدة البيانات"""
        
        tables = [
            # جدول المستخدمين
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # جدول الفئات
            """CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )""",
            
            # جدول التجار الخارجيين
            """CREATE TABLE IF NOT EXISTS external_traders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                email TEXT,
                shop_percentage REAL DEFAULT 20.0,
                trader_percentage REAL DEFAULT 80.0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # جدول الموردين
            """CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                address TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # جدول المنتجات
            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                sell_price REAL NOT NULL,
                cost_price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 5,
                barcode TEXT UNIQUE,
                description TEXT,
                supplier_id INTEGER,
                external_trader_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                FOREIGN KEY (external_trader_id) REFERENCES external_traders (id)
            )""",

            # جدول تتبع عمليات المنتجات (إضافة/تحديث/تعديل)
            """CREATE TABLE IF NOT EXISTS product_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                action TEXT NOT NULL, -- add/update/modify
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )""",
            
            # جدول العملاء
            """CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                email TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # جدول المبيعات
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                customer_id INTEGER,
                total_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                payment_method TEXT DEFAULT 'نقدي',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )""",
            
            # جدول عناصر المبيعات
            """CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_at_sale REAL NOT NULL,
                cost_at_sale REAL NOT NULL,
                discount REAL DEFAULT 0,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )""",
            
            # جدول المصروفات
            """CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT 'عام',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )""",
            
            # جدول المشتريات
            """CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                invoice_number TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )""",
            
            # جدول المرتجعات
            """CREATE TABLE IF NOT EXISTS returns (
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
            )"""
        ]
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for table_sql in tables:
                cursor.execute(table_sql)
            conn.commit()
        
        print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
