"""
متحكم المشتريات
"""
from database.connection import db
from utils.helpers import get_current_datetime
from controllers.product_controller import ProductController


class PurchaseController:
    """متحكم المشتريات"""
    
    @staticmethod
    def add_purchase(product_id, quantity, cost_price, supplier_id=None, invoice_number="", notes=""):
        """إضافة مشترى جديد"""
        try:
            total_amount = quantity * cost_price
            
            # إضافة المشترى
            db.execute(
                """INSERT INTO purchases 
                   (supplier_id, product_id, quantity, cost_price, total_amount, 
                    invoice_number, notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (supplier_id, product_id, quantity, cost_price, total_amount,
                 invoice_number, notes, get_current_datetime())
            )
            
            # تحديث المخزون
            result = ProductController.update_stock(product_id, quantity, 'add')
            
            if not result['success']:
                return result
            
            return {'success': True, 'message': 'تم إضافة المشترى بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_all_purchases(start_date=None, end_date=None, limit=100):
        """الحصول على جميع المشتريات"""
        if start_date and end_date:
            return db.fetch_all(
                """SELECT p.*, pr.name as product_name, s.name as supplier_name
                   FROM purchases p
                   LEFT JOIN products pr ON p.product_id = pr.id
                   LEFT JOIN suppliers s ON p.supplier_id = s.id
                   WHERE DATE(p.created_at) BETWEEN ? AND ?
                   ORDER BY p.created_at DESC
                   LIMIT ?""",
                (start_date, end_date, limit)
            )
        else:
            return db.fetch_all(
                """SELECT p.*, pr.name as product_name, s.name as supplier_name
                   FROM purchases p
                   LEFT JOIN products pr ON p.product_id = pr.id
                   LEFT JOIN suppliers s ON p.supplier_id = s.id
                   ORDER BY p.created_at DESC
                   LIMIT ?""",
                (limit,)
            )
    
    @staticmethod
    def get_today_purchases():
        """مشتريات اليوم"""
        result = db.fetch_one(
            """SELECT SUM(total_amount) as total, COUNT(*) as count
               FROM purchases
               WHERE DATE(created_at) = DATE('now')"""
        )
        return {
            'total': result['total'] or 0,
            'count': result['count'] or 0
        }
    
    @staticmethod
    def delete_purchase(purchase_id):
        """حذف مشترى"""
        try:
            # الحصول على بيانات المشترى
            purchase = db.fetch_one(
                "SELECT * FROM purchases WHERE id = ?",
                (purchase_id,)
            )
            
            if not purchase:
                return {'success': False, 'message': 'المشترى غير موجود'}
            
            # تقليل المخزون
            ProductController.update_stock(
                purchase['product_id'], 
                purchase['quantity'], 
                'subtract'
            )
            
            # حذف المشترى
            db.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
            
            return {'success': True, 'message': 'تم حذف المشترى'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_suppliers():
        """الحصول على جميع الموردين"""
        return db.fetch_all("SELECT * FROM suppliers ORDER BY name")
    
    @staticmethod
    def add_supplier(name, phone="", company="", address="", email=""):
        """إضافة مورد جديد"""
        try:
            db.execute(
                """INSERT INTO suppliers (name, phone, company, address, email)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, phone, company, address, email)
            )
            return {'success': True, 'message': 'تم إضافة المورد بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def process_bulk_purchase(supplier_id, items, user_id=None):
        """معالجة عملية شراء متعددة المنتجات"""
        try:
            if not items:
                return {'success': False, 'message': 'لا توجد منتجات للشراء'}
            
            total_cost = 0
            invoice_number = f"BULK-{get_current_datetime().replace(':', '').replace(' ', '-')}"
            
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                cost_price = item['cost_price']
                total_amount = item['total']
                
                # إضافة المشترى
                db.execute(
                    """INSERT INTO purchases 
                       (supplier_id, product_id, quantity, cost_price, total_amount, 
                        invoice_number, notes, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (supplier_id, product_id, quantity, cost_price, total_amount,
                     invoice_number, "عملية شراء متعددة", get_current_datetime())
                )
                
                # تحديث المخزون
                result = ProductController.update_stock(product_id, quantity, 'add')
                if not result['success']:
                    return result
                
                total_cost += total_amount
            
            return {
                'success': True, 
                'message': f'تم شراء {len(items)} منتج بنجاح - الإجمالي: {total_cost:,.2f} جنيه'
            }
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
