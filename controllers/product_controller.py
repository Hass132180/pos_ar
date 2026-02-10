"""
متحكم إدارة المنتجات
"""
from database.connection import db
from utils.helpers import get_current_datetime


class ProductController:
    """متحكم المنتجات"""
    
    @staticmethod
    def get_all_products(search_query="", category_id=None):
        """الحصول على جميع المنتجات مع إمكانية التصفية بالقسم"""
        base_query = """SELECT p.*, c.name as category_name, 
                       COALESCE(et.name, 'بدون تاجر') as trader_name
                       FROM products p
                       LEFT JOIN categories c ON p.category_id = c.id
                       LEFT JOIN external_traders et ON p.external_trader_id = et.id"""
        
        conditions = []
        params = []
        
        # إضافة شرط البحث النصي
        if search_query:
            conditions.append("(p.name LIKE ? OR p.barcode LIKE ?)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        # إضافة شرط التصفية بالقسم
        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        
        # بناء الاستعلام النهائي
        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY p.name"
        else:
            query = f"{base_query} ORDER BY p.name"
        
        return db.fetch_all(query, params)
    
    @staticmethod
    def get_product_by_id(product_id):
        """الحصول على منتج بالمعرف"""
        return db.fetch_one(
            """SELECT p.*, c.name as category_name,
               s.name as supplier_name,
               et.name as trader_name
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.id
               LEFT JOIN suppliers s ON p.supplier_id = s.id
               LEFT JOIN external_traders et ON p.external_trader_id = et.id
               WHERE p.id = ?""",
            (product_id,)
        )
    
    @staticmethod
    def get_product_by_barcode(barcode):
        """الحصول على منتج بالباركود"""
        return db.fetch_one(
            "SELECT * FROM products WHERE barcode = ?",
            (barcode,)
        )
    
    @staticmethod
    def add_product(data):
        """إضافة منتج جديد"""
        try:
            # التحقق من عدم تكرار الباركود
            if data.get('barcode'):
                existing = db.fetch_one(
                    "SELECT id FROM products WHERE barcode = ?",
                    (data['barcode'],)
                )
                if existing:
                    return {'success': False, 'message': 'الباركود موجود بالفعل'}
            
            db.execute(
                """INSERT INTO products 
                   (name, category_id, sell_price, cost_price, stock, barcode, 
                    description, supplier_id, external_trader_id, min_stock)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data['name'], data['category_id'], data['sell_price'], 
                 data['cost_price'], data.get('stock', 0), data.get('barcode') or None,
                 data.get('description', ''), data.get('supplier_id'), 
                 data.get('external_trader_id'), data.get('min_stock', 5))
            )
            
            return {'success': True, 'message': 'تم إضافة المنتج بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def update_product(product_id, **kwargs):
        """تحديث منتج"""
        try:
            allowed_fields = ['name', 'category_id', 'sell_price', 'cost_price', 
                            'stock', 'barcode', 'description', 'supplier_id', 
                            'external_trader_id', 'min_stock']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'message': 'لا توجد حقول للتحديث'}
            
            values.append(product_id)
            
            db.execute(
                f"UPDATE products SET {', '.join(updates)} WHERE id = ?",
                values
            )
            
            return {'success': True, 'message': 'تم تحديث المنتج بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def delete_product(product_id):
        """حذف منتج"""
        try:
            db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return {'success': True, 'message': 'تم حذف المنتج بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def update_stock(product_id, quantity, operation='add'):
        """تحديث المخزون"""
        try:
            product = ProductController.get_product_by_id(product_id)
            if not product:
                return {'success': False, 'message': 'المنتج غير موجود'}
            
            current_stock = product['stock']
            
            if operation == 'add':
                new_stock = current_stock + quantity
            elif operation == 'subtract':
                if current_stock < quantity:
                    return {'success': False, 'message': 'المخزون غير كافي'}
                new_stock = current_stock - quantity
            else:
                new_stock = quantity
            
            db.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, product_id)
            )
            
            return {'success': True, 'new_stock': new_stock}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_low_stock_products():
        """الحصول على المنتجات منخفضة المخزون"""
        return db.fetch_all(
            "SELECT * FROM products WHERE stock <= min_stock ORDER BY stock"
        )
    
    @staticmethod
    def get_total_inventory_value():
        """حساب إجمالي قيمة المخزون"""
        result = db.fetch_one(
            "SELECT SUM(stock * cost_price) as total_cost, SUM(stock * sell_price) as total_sell FROM products"
        )
        return {
            'total_cost': result['total_cost'] or 0,
            'total_sell': result['total_sell'] or 0,
            'expected_profit': (result['total_sell'] or 0) - (result['total_cost'] or 0)
        }
    
    @staticmethod
    def get_all_categories():
        """الحصول على جميع الأقسام"""
        return db.fetch_all("SELECT * FROM categories ORDER BY name")
