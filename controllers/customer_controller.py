"""
متحكم إدارة العملاء
"""
from database.connection import db


class CustomerController:
    """متحكم العملاء"""
    
    @staticmethod
    def get_all_customers(search_query=""):
        """الحصول على جميع العملاء"""
        if search_query:
            return db.fetch_all(
                """SELECT * FROM customers 
                   WHERE name LIKE ? OR phone LIKE ?
                   ORDER BY name""",
                (f"%{search_query}%", f"%{search_query}%")
            )
        else:
            return db.fetch_all("SELECT * FROM customers ORDER BY name")
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """الحصول على عميل بالمعرف"""
        return db.fetch_one(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        )
    
    @staticmethod
    def add_customer(name, phone="", address="", email="", notes=""):
        """إضافة عميل جديد"""
        try:
            db.execute(
                """INSERT INTO customers (name, phone, address, email, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, phone, address, email, notes)
            )
            
            return {'success': True, 'message': 'تم إضافة العميل بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def update_customer(customer_id, **kwargs):
        """تحديث عميل"""
        try:
            allowed_fields = ['name', 'phone', 'address', 'email', 'notes']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'message': 'لا توجد حقول للتحديث'}
            
            values.append(customer_id)
            
            db.execute(
                f"UPDATE customers SET {', '.join(updates)} WHERE id = ?",
                values
            )
            
            return {'success': True, 'message': 'تم تحديث العميل بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def delete_customer(customer_id):
        """حذف عميل"""
        try:
            db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            return {'success': True, 'message': 'تم حذف العميل بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_customer_purchases(customer_id):
        """الحصول على مشتريات العميل"""
        return db.fetch_all(
            """SELECT * FROM sales 
               WHERE customer_id = ?
               ORDER BY created_at DESC""",
            (customer_id,)
        )
