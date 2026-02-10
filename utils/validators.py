"""
دوال التحقق من صحة البيانات
"""
import re
from datetime import datetime


def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """التحقق من صحة رقم الهاتف المصري"""
    # إزالة المسافات والرموز
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # التحقق من الصيغة
    pattern = r'^(01)[0-9]{9}$'
    return bool(re.match(pattern, phone))


def validate_number(value, min_value=None, max_value=None):
    """التحقق من صحة رقم"""
    try:
        num = float(value)
        
        if min_value is not None and num < min_value:
            return False
        
        if max_value is not None and num > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_required(value):
    """التحقق من أن الحقل غير فارغ"""
    if value is None:
        return False
    
    if isinstance(value, str):
        return bool(value.strip())
    
    return True


def validate_date(date_str, date_format='%Y-%m-%d'):
    """التحقق من صحة التاريخ"""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except (ValueError, TypeError):
        return False


def validate_username(username):
    """التحقق من صحة اسم المستخدم"""
    if not username or len(username) < 3:
        return False
    
    # يجب أن يحتوي على حروف وأرقام فقط
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def validate_password(password):
    """التحقق من قوة كلمة المرور"""
    if not password or len(password) < 6:
        return False
    
    return True


def validate_barcode(barcode):
    """التحقق من صحة الباركود"""
    if not barcode:
        return False
    
    # يمكن أن يحتوي على أرقام وحروف
    pattern = r'^[a-zA-Z0-9]{3,50}$'
    return bool(re.match(pattern, barcode))


def sanitize_input(text):
    """تنظيف المدخلات من الأحرف الخطرة"""
    if not text:
        return ""
    
    # إزالة العلامات الخطرة
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


def format_currency(amount):
    """تنسيق المبلغ المالي"""
    try:
        return f"{float(amount):,.2f} جنيه"
    except (ValueError, TypeError):
        return "0.00 جنيه"


def format_percentage(value):
    """تنسيق النسبة المئوية"""
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_date(date_obj, format_str='%Y-%m-%d'):
    """تنسيق التاريخ"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    
    return str(date_obj)
