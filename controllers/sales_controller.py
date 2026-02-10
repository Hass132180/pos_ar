"""
متحكم إدارة المبيعات
"""
from database.connection import db
from utils.helpers import generate_invoice_number, get_current_datetime, calculate_trader_share
from controllers.product_controller import ProductController


class SalesController:
    """متحكم المبيعات"""
    
    @staticmethod
    def create_sale(user_id, items, customer_id=None, discount=0, payment_method='نقدي', notes=""):
        """إنشاء عملية بيع جديدة"""
        try:
            # حساب الإجمالي
            total_amount = 0
            for item in items:
                total_amount += item['price'] * item['quantity'] - item.get('discount', 0)
            
            total_amount -= discount
            
            if total_amount <= 0:
                return {'success': False, 'message': 'المبلغ الإجمالي غير صحيح'}
            
            # توليد رقم فاتورة
            invoice_number = generate_invoice_number()
            
            # إنشاء الفاتورة
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # إدراج الفاتورة
                cursor.execute(
                    """INSERT INTO sales (invoice_number, user_id, customer_id, total_amount, 
                       discount, payment_method, notes, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (invoice_number, user_id, customer_id, total_amount, discount, 
                     payment_method, notes, get_current_datetime())
                )
                
                sale_id = cursor.lastrowid
                
                # إدراج عناصر الفاتورة وتحديث المخزون
                for item in items:
                    product = ProductController.get_product_by_id(item['product_id'])
                    
                    if not product:
                        conn.rollback()
                        return {'success': False, 'message': f'المنتج {item["product_id"]} غير موجود'}
                    
                    if product['stock'] < item['quantity']:
                        conn.rollback()
                        return {'success': False, 'message': f'مخزون {product["name"]} غير كافي'}
                    
                    item_total = item['price'] * item['quantity'] - item.get('discount', 0)
                    
                    cursor.execute(
                        """INSERT INTO sale_items (sale_id, product_id, quantity, price_at_sale, 
                           cost_at_sale, discount, total_price)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (sale_id, item['product_id'], item['quantity'], item['price'],
                         product['cost_price'], item.get('discount', 0), item_total)
                    )
                    
                    # تحديث المخزون
                    new_stock = product['stock'] - item['quantity']
                    cursor.execute(
                        "UPDATE products SET stock = ? WHERE id = ?",
                        (new_stock, item['product_id'])
                    )
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'تمت عملية البيع بنجاح',
                    'sale_id': sale_id,
                    'invoice_number': invoice_number,
                    'total': total_amount
                }
        
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_sale_by_id(sale_id):
        """الحصول على فاتورة"""
        sale = db.fetch_one(
            """SELECT s.*, u.full_name as user_name, c.name as customer_name
               FROM sales s
               LEFT JOIN users u ON s.user_id = u.id
               LEFT JOIN customers c ON s.customer_id = c.id
               WHERE s.id = ?""",
            (sale_id,)
        )
        
        if sale:
            items = db.fetch_all(
                """SELECT si.*, p.name as product_name
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   WHERE si.sale_id = ?""",
                (sale_id,)
            )
            
            return {'sale': dict(sale), 'items': [dict(item) for item in items]}
        
        return None
    
    @staticmethod
    def get_all_sales(start_date=None, end_date=None, limit=100):
        """الحصول على جميع المبيعات"""
        if start_date and end_date:
            return db.fetch_all(
                """SELECT s.*, u.full_name as user_name, c.name as customer_name
                   FROM sales s
                   LEFT JOIN users u ON s.user_id = u.id
                   LEFT JOIN customers c ON s.customer_id = c.id
                   WHERE DATE(s.created_at) BETWEEN ? AND ?
                   ORDER BY s.created_at DESC
                   LIMIT ?""",
                (start_date, end_date, limit)
            )
        else:
            return db.fetch_all(
                """SELECT s.*, u.full_name as user_name, c.name as customer_name
                   FROM sales s
                   LEFT JOIN users u ON s.user_id = u.id
                   LEFT JOIN customers c ON s.customer_id = c.id
                   ORDER BY s.created_at DESC
                   LIMIT ?""",
                (limit,)
            )
    
    @staticmethod
    def get_today_sales():
        """مبيعات اليوم"""
        return db.fetch_all(
            """SELECT s.*, u.full_name as user_name
               FROM sales s
               LEFT JOIN users u ON s.user_id = u.id
               WHERE DATE(s.created_at) = DATE('now')
               ORDER BY s.created_at DESC"""
        )
    
    @staticmethod
    def get_sales_summary(start_date=None, end_date=None):
        """ملخص المبيعات"""
        if start_date and end_date:
            result = db.fetch_one(
                """SELECT 
                   COUNT(*) as total_sales,
                   SUM(total_amount) as total_revenue,
                   SUM(discount) as total_discount,
                   AVG(total_amount) as avg_sale
                   FROM sales
                   WHERE DATE(created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            )
        else:
            result = db.fetch_one(
                """SELECT 
                   COUNT(*) as total_sales,
                   SUM(total_amount) as total_revenue,
                   SUM(discount) as total_discount,
                   AVG(total_amount) as avg_sale
                   FROM sales
                   WHERE DATE(created_at) = DATE('now')"""
            )
        
        return dict(result) if result else {}
    
    @staticmethod
    def calculate_profit(start_date=None, end_date=None):
        """حساب الأرباح"""
        if start_date and end_date:
            result = db.fetch_one(
                """SELECT 
                   SUM(si.total_price) as total_revenue,
                   SUM(si.cost_at_sale * si.quantity) as total_cost
                   FROM sale_items si
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) BETWEEN ? AND ?""",
                (start_date, end_date)
            )
        else:
            result = db.fetch_one(
                """SELECT 
                   SUM(si.total_price) as total_revenue,
                   SUM(si.cost_at_sale * si.quantity) as total_cost
                   FROM sale_items si
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) = DATE('now')"""
            )
        
        if result and result['total_revenue']:
            total_revenue = result['total_revenue'] or 0
            total_cost = result['total_cost'] or 0
            profit = total_revenue - total_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'profit': profit,
                'profit_margin': profit_margin
            }
        
        return {'total_revenue': 0, 'total_cost': 0, 'profit': 0, 'profit_margin': 0}
    
    @staticmethod
    def return_sale_item(sale_id, product_id, quantity, user_id=None, reason=""):
        """استرجاع منتج من بيع"""
        try:
            # استخدام transaction للتأكد من تطبيق كل العمليات
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # التحقق من وجود العنصر في البيع
                cursor.execute(
                    "SELECT * FROM sale_items WHERE sale_id = ? AND product_id = ?",
                    (sale_id, product_id)
                )
                sale_item = cursor.fetchone()
                
                if not sale_item:
                    return False
                
                # تحويل Row إلى dict للوصول السهل
                sale_item = dict(sale_item)
                
                if quantity > sale_item['quantity']:
                    return False
                
                # حساب مبلغ المرتجع
                return_amount = quantity * sale_item['price_at_sale']
                
                # تسجيل المرتجع في جدول المرتجعات
                cursor.execute(
                    """INSERT INTO returns (sale_id, product_id, quantity, return_amount, user_id, reason, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (sale_id, product_id, quantity, return_amount, user_id or 1, reason)
                )
                
                # تحديث أو حذف العنصر من البيع
                if quantity == sale_item['quantity']:
                    # حذف العنصر كاملاً
                    cursor.execute("DELETE FROM sale_items WHERE sale_id = ? AND product_id = ?", 
                              (sale_id, product_id))
                else:
                    # تقليل الكمية
                    new_quantity = sale_item['quantity'] - quantity
                    new_total = new_quantity * sale_item['price_at_sale']
                    cursor.execute(
                        "UPDATE sale_items SET quantity = ?, total_price = ? WHERE sale_id = ? AND product_id = ?",
                        (new_quantity, new_total, sale_id, product_id)
                    )
                
                # تحديث إجمالي البيع
                cursor.execute(
                    "SELECT SUM(total_price) as total FROM sale_items WHERE sale_id = ?",
                    (sale_id,)
                )
                remaining_items = cursor.fetchone()
                
                new_sale_total = remaining_items['total'] if remaining_items['total'] else 0
                cursor.execute("UPDATE sales SET total_amount = ? WHERE id = ?", 
                          (new_sale_total, sale_id))
                
                # إعادة المنتج للمخزون
                cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
                product = cursor.fetchone()
                if product:
                    current_stock = product['stock']
                    new_stock = current_stock + quantity
                    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
                else:
                    return False
                
                # تطبيق كل التغييرات
                conn.commit()
                return True
            
        except Exception as e:
            print(f"خطأ في المرتجعات: {str(e)}")
            return False
    
    @staticmethod
    def get_returns_summary(period='today'):
        """الحصول على ملخص المرتجعات"""
        try:
            date_filter = ""
            if period == 'today':
                date_filter = "AND DATE(r.created_at) = DATE('now')"
            elif period == 'week':
                date_filter = "AND DATE(r.created_at) >= DATE('now', '-7 days')"
            elif period == 'month':
                date_filter = "AND DATE(r.created_at) >= DATE('now', '-30 days')"
            
            result = db.fetch_one(f"""
                SELECT 
                    COUNT(*) as total_returns,
                    SUM(r.quantity) as total_quantity,
                    SUM(r.return_amount) as total_amount
                FROM returns r
                WHERE 1=1 {date_filter}
            """)
            
            return {
                'total_returns': result['total_returns'] or 0,
                'total_quantity': result['total_quantity'] or 0,
                'total_amount': result['total_amount'] or 0
            }
            
        except Exception as e:
            print(f"خطأ في جلب إحصائيات المرتجعات: {e}")
            return {'total_returns': 0, 'total_quantity': 0, 'total_amount': 0}
