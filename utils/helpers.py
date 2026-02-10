"""
دوال مساعدة عامة
"""
import hashlib
from datetime import datetime, timedelta
import json


def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """التحقق من كلمة المرور"""
    return hash_password(password) == hashed


def get_current_datetime():
    """الحصول على التاريخ والوقت الحالي"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_current_date():
    """الحصول على التاريخ الحالي"""
    return datetime.now().strftime('%Y-%m-%d')


def get_date_range(days_back=30):
    """الحصول على نطاق تاريخ"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return {
        'start': start_date.strftime('%Y-%m-%d'),
        'end': end_date.strftime('%Y-%m-%d')
    }


def calculate_profit(sale_price, purchase_price, quantity=1):
    """حساب الربح"""
    total_sale = sale_price * quantity
    total_cost = purchase_price * quantity
    profit = total_sale - total_cost
    
    if total_cost > 0:
        profit_percentage = (profit / total_cost) * 100
    else:
        profit_percentage = 0
    
    return {
        'profit': profit,
        'percentage': profit_percentage,
        'total_sale': total_sale,
        'total_cost': total_cost
    }


def calculate_trader_share(total_profit, shop_percentage):
    """حساب حصة التاجر والمحل"""
    shop_share = total_profit * (shop_percentage / 100)
    trader_share = total_profit - shop_share
    
    return {
        'shop_share': shop_share,
        'trader_share': trader_share,
        'total_profit': total_profit
    }


def generate_invoice_number():
    """توليد رقم فاتورة"""
    now = datetime.now()
    return f"INV-{now.strftime('%Y%m%d%H%M%S')}"


def export_to_json(data, filename):
    """تصدير البيانات إلى JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"خطأ في التصدير: {e}")
        return False


def import_from_json(filename):
    """استيراد البيانات من JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"خطأ في الاستيراد: {e}")
        return None


def format_currency(amount):
    """تنسيق المبلغ المالي"""
    try:
        return f"{float(amount):,.2f} جنيه"
    except (ValueError, TypeError):
        return "0.00 جنيه"


def truncate_text(text, max_length=50):
    """اختصار النص"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def search_in_list(items, query, fields):
    """البحث في قائمة من القواميس"""
    query = query.lower()
    results = []
    
    for item in items:
        for field in fields:
            if field in item:
                value = str(item[field]).lower()
                if query in value:
                    results.append(item)
                    break
    
    return results


def sort_dict_list(items, key, reverse=False):
    """ترتيب قائمة من القواميس"""
    return sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)


def group_by_field(items, field):
    """تجميع العناصر حسب حقل"""
    groups = {}
    
    for item in items:
        key = item.get(field, 'other')
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    
    return groups


def calculate_total(items, field):
    """حساب المجموع لحقل معين"""
    total = 0
    for item in items:
        try:
            total += float(item.get(field, 0))
        except (ValueError, TypeError):
            continue
    
    return total


def calculate_average(items, field):
    """حساب المتوسط لحقل معين"""
    if not items:
        return 0
    
    total = calculate_total(items, field)
    return total / len(items)


def get_top_items(items, field, limit=10, reverse=True):
    """الحصول على أعلى العناصر"""
    sorted_items = sort_dict_list(items, field, reverse)
    return sorted_items[:limit]


def filter_by_date_range(items, date_field, start_date, end_date):
    """تصفية العناصر حسب نطاق تاريخ"""
    results = []
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        for item in items:
            item_date_str = item.get(date_field, '')
            if not item_date_str:
                continue
            
            try:
                item_date = datetime.strptime(item_date_str.split()[0], '%Y-%m-%d')
                if start <= item_date <= end:
                    results.append(item)
            except ValueError:
                continue
    
    except ValueError:
        return items
    
    return results
