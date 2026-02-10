"""
متحكم المصادقة وإدارة المستخدمين
"""
from database.connection import db
from utils.helpers import hash_password, verify_password


class AuthController:
    """متحكم المصادقة"""
    
    @staticmethod
    def login(username, password):
        """تسجيل الدخول"""
        user = db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        
        if user and verify_password(password, user['password']):
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
            }
        
        return {
            'success': False,
            'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'
        }
    
    @staticmethod
    def create_user(username, password, full_name, role='cashier'):
        """إنشاء مستخدم جديد"""
        try:
            # التحقق من عدم وجود المستخدم
            existing = db.fetch_one(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            )
            if existing:
                return {
                    'success': False,
                    'message': 'اسم المستخدم موجود بالفعل'
                }
            
            # إضافة المستخدم
            hashed_pwd = hash_password(password)
            db.execute(
                """INSERT INTO users (username, password, full_name, role)
                   VALUES (?, ?, ?, ?)""",
                (username, hashed_pwd, full_name, role)
            )
            
            return {
                'success': True,
                'message': 'تم إضافة المستخدم بنجاح'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في إضافة المستخدم: {str(e)}'
            }
    
    @staticmethod
    def get_all_users():
        """الحصول على جميع المستخدمين"""
        return db.fetch_all(
            "SELECT id, username, full_name, role, is_active, created_at FROM users"
        )
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """تحديث بيانات مستخدم"""
        try:
            allowed_fields = ['full_name', 'role', 'is_active']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'message': 'لا توجد حقول للتحديث'}
            
            values.append(user_id)
            
            db.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                values
            )
            
            return {'success': True, 'message': 'تم التحديث بنجاح'}
        
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def change_password(user_id, old_password, new_password, is_admin=False):
        """تغيير كلمة المرور"""
        try:
            user = db.fetch_one(
                "SELECT password FROM users WHERE id = ?",
                (user_id,)
            )
            
            if not user:
                return {'success': False, 'message': 'المستخدم غير موجود'}
            
            # إذا كان المدير يغير كلمة مرور مستخدم آخر، لا نحتاج للتحقق من كلمة المرور القديمة
            if not is_admin:
                if not verify_password(old_password, user['password']):
                    return {'success': False, 'message': 'كلمة المرور القديمة غير صحيحة'}
            
            hashed_pwd = hash_password(new_password)
            db.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed_pwd, user_id)
            )
            
            return {'success': True, 'message': 'تم تغيير كلمة المرور بنجاح'}
        
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
    
    @staticmethod
    def delete_user(user_id):
        """حذف مستخدم نهائياً"""
        try:
            # التحقق من عدم حذف المستخدم الحالي
            db.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            
            return {'success': True, 'message': 'تم حذف المستخدم بنجاح'}
        
        except Exception as e:
            return {'success': False, 'message': f'خطأ: {str(e)}'}
