"""
متحكم إدارة التجار الخارجيين
"""
from database.connection import db
from utils.helpers import calculate_trader_share


class TraderController:
    """متحكم التجار الخارجيين"""
    
    @staticmethod
    def get_all_traders(search_query=""):
        """الحصول على جميع التجار"""
        if search_query:
            return db.fetch_all(
                """SELECT * FROM external_traders 
                   WHERE name LIKE ? OR phone LIKE ?
                   ORDER BY name""",
                (f"%{search_query}%", f"%{search_query}%")
            )
        else:
            return db.fetch_all("SELECT * FROM external_traders ORDER BY name")
    
    @staticmethod
    def get_trader_by_id(trader_id):
        """الحصول على تاجر بالمعرف"""
        return db.fetch_one(
            "SELECT * FROM external_traders WHERE id = ?",
            (trader_id,)
        )
    
    @staticmethod
    def add_trader(name, phone="", address="", email="", shop_percentage=20.0, notes=""):
        """إضافة تاجر جديد"""
        try:
            trader_percentage = 100.0 - shop_percentage
            
            db.execute(
                """INSERT INTO external_traders 
                   (name, phone, address, email, shop_percentage, trader_percentage, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, phone, address, email, shop_percentage, trader_percentage, notes)
            )
            
            return {'success': True, 'message': 'تم إضافة التاجر بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def update_trader(trader_id, **kwargs):
        """تحديث تاجر"""
        try:
            # إذا تم تحديث نسبة المحل، نحدث نسبة التاجر تلقائياً
            if 'shop_percentage' in kwargs:
                kwargs['trader_percentage'] = 100.0 - kwargs['shop_percentage']
            
            allowed_fields = ['name', 'phone', 'address', 'email', 
                            'shop_percentage', 'trader_percentage', 'notes']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'message': 'لا توجد حقول للتحديث'}
            
            values.append(trader_id)
            
            db.execute(
                f"UPDATE external_traders SET {', '.join(updates)} WHERE id = ?",
                values
            )
            
            return {'success': True, 'message': 'تم تحديث التاجر بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def delete_trader(trader_id):
        """حذف تاجر"""
        try:
            db.execute("DELETE FROM external_traders WHERE id = ?", (trader_id,))
            return {'success': True, 'message': 'تم حذف التاجر بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_trader_products(trader_id):
        """الحصول على منتجات التاجر"""
        return db.fetch_all(
            """SELECT p.*, c.name as category_name
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.external_trader_id = ?
               ORDER BY p.name""",
            (trader_id,)
        )
    
    @staticmethod
    def calculate_trader_profits(trader_id, start_date=None, end_date=None):
        """حساب أرباح التاجر"""
        trader = TraderController.get_trader_by_id(trader_id)
        if not trader:
            return None
        
        # الحصول على مبيعات منتجات التاجر
        if start_date and end_date:
            sales = db.fetch_all(
                """SELECT si.*, p.name as product_name
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE p.external_trader_id = ?
                   AND DATE(s.created_at) BETWEEN ? AND ?""",
                (trader_id, start_date, end_date)
            )
        else:
            sales = db.fetch_all(
                """SELECT si.*, p.name as product_name
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE p.external_trader_id = ?""",
                (trader_id,)
            )
        
        total_profit = 0
        for sale in sales:
            item_profit = (sale['price_at_sale'] - sale['cost_at_sale']) * sale['quantity']
            total_profit += item_profit
        
        # حساب الحصص
        shares = calculate_trader_share(total_profit, trader['shop_percentage'])
        
        return {
            'trader_name': trader['name'],
            'total_sales': len(sales),
            'total_profit': total_profit,
            'shop_share': shares['shop_share'],
            'trader_share': shares['trader_share'],
            'shop_percentage': trader['shop_percentage'],
            'trader_percentage': trader['trader_percentage']
        }
    
    @staticmethod
    def get_all_traders_report(start_date=None, end_date=None):
        """تقرير جميع التجار"""
        traders = TraderController.get_all_traders()
        report = []
        
        for trader in traders:
            profits = TraderController.calculate_trader_profits(
                trader['id'], start_date, end_date
            )
            if profits:
                report.append(profits)
        
        return report
