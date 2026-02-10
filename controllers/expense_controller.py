"""
متحكم المصروفات
"""
from database.connection import db
from utils.helpers import get_current_datetime


class ExpenseController:
    """متحكم المصروفات"""
    
    @staticmethod
    def add_expense(user_id, amount, description, category="عام"):
        """إضافة مصروف"""
        try:
            db.execute(
                """INSERT INTO expenses (user_id, amount, description, category, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, amount, description, category, get_current_datetime())
            )
            return {'success': True, 'message': 'تم إضافة المصروف بنجاح'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def get_all_expenses(start_date=None, end_date=None):
        """الحصول على جميع المصروفات"""
        if start_date and end_date:
            return db.fetch_all(
                """SELECT e.*, u.full_name as user_name
                   FROM expenses e
                   LEFT JOIN users u ON e.user_id = u.id
                   WHERE DATE(e.created_at) BETWEEN ? AND ?
                   ORDER BY e.created_at DESC""",
                (start_date, end_date)
            )
        else:
            return db.fetch_all(
                """SELECT e.*, u.full_name as user_name
                   FROM expenses e
                   LEFT JOIN users u ON e.user_id = u.id
                   ORDER BY e.created_at DESC
                   LIMIT 100"""
            )
    
    @staticmethod
    def get_today_expenses():
        """مصروفات اليوم"""
        result = db.fetch_one(
            """SELECT SUM(amount) as total, COUNT(*) as count
               FROM expenses
               WHERE DATE(created_at) = DATE('now')"""
        )
        return {
            'total': result['total'] or 0,
            'count': result['count'] or 0
        }
    
    @staticmethod
    def get_today_total():
        """إجمالي مصروفات اليوم (للاستخدام السريع)"""
        result = db.fetch_one(
            """SELECT SUM(amount) as total
               FROM expenses
               WHERE DATE(created_at) = DATE('now')"""
        )
        return result['total'] or 0
    
    @staticmethod
    def delete_expense(expense_id):
        """حذف مصروف"""
        try:
            db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            return {'success': True, 'message': 'تم حذف المصروف'}
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
