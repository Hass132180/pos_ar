"""
أداة استيراد البيانات من ملف SQL إلى قاعدة بيانات البرنامج
تحويل البيانات من back/pos_system.db.sql إلى pos_system.db
"""

import sqlite3
import os
import re
from datetime import datetime

def parse_sql_file(sql_file_path):
    """قراءة وتحليل ملف SQL"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # استخراج جمل INSERT
    insert_pattern = r'INSERT INTO "(\w+)".*?VALUES\s+(.*?);'
    matches = re.findall(insert_pattern, sql_content, re.DOTALL | re.MULTILINE)
    
    data_dict = {}
    for table_name, values_str in matches:
        if table_name not in data_dict:
            data_dict[table_name] = []
        
        # تحليل القيم - تعامل مع القيم المتعددة
        rows = []
        current_row = []
        in_string = False
        paren_depth = 0
        current_value = ''
        
        for char in values_str:
            if char == "'" and (not current_value or current_value[-1] != '\\'):
                in_string = not in_string
                current_value += char
            elif char == '(' and not in_string:
                paren_depth += 1
                if paren_depth == 1:
                    current_value = ''
            elif char == ')' and not in_string:
                paren_depth -= 1
                if paren_depth == 0:
                    if current_value:
                        current_row.append(current_value.strip())
                    rows.append(current_row)
                    current_row = []
                    current_value = ''
            elif char == ',' and not in_string:
                if paren_depth > 0:
                    current_row.append(current_value.strip())
                    current_value = ''
            else:
                current_value += char
        
        data_dict[table_name].extend(rows)
    
    return data_dict

def clean_value(value):
    """تنظيف القيمة من علامات الاقتباس والمسافات"""
    value = value.strip()
    if value == 'NULL':
        return None
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
        # استبدال العلامات المحمية
        value = value.replace("''", "'")
    return value

def get_table_column_mapping():
    """مطابقة أعمدة ملف SQL القديم مع الجداول الجديدة"""
    return {
        'categories': ['id', 'name'],  # الجدول القديم: id, name
        'users': ['id', 'username', 'password', 'role', 'full_name', 'is_active'],  # القديم: id, username, password_hash, role, full_name, active
        'customers': ['id', 'name', 'phone', 'address', 'email', 'notes', 'created_at'],
        'external_traders': ['id', 'name', 'phone', 'address', 'email', 'shop_percentage', 'trader_percentage', 'notes', 'created_at'],
        'suppliers': ['id', 'name', 'phone', 'company', 'address'],  # القديم: id, name, phone, company, address
        'products': ['id', 'name', 'category_id', 'sell_price', 'cost_price', 'stock'],  # القديم: id, name, category_id, sell_price, cost_price, stock
        'sales': ['id', 'invoice_number', 'user_id', 'total_amount', 'created_at'],  # القديم: sale_date → الجديد: created_at
        'sale_items': ['id', 'sale_id', 'product_id', 'quantity', 'price_at_sale', 'cost_at_sale', 'total_price'],
        'expenses': ['id', 'user_id', 'amount', 'description', 'created_at'],  # القديم: expense_date → الجديد: created_at
        'purchases': ['id', 'supplier_id', 'product_id', 'quantity', 'cost_price', 'total_amount', 'created_at']  # القديم: purchase_date → الجديد: created_at
    }

def import_data_to_database(sql_file_path, db_path):
    """استيراد البيانات من ملف SQL إلى قاعدة البيانات"""
    
    print("🔄 بدء عملية استيراد البيانات...")
    
    # التحقق من وجود ملف SQL
    if not os.path.exists(sql_file_path):
        print(f"❌ خطأ: ملف SQL غير موجود: {sql_file_path}")
        return False
    
    # قراءة البيانات من ملف SQL
    print("📖 قراءة البيانات من ملف SQL...")
    data_dict = parse_sql_file(sql_file_path)
    
    # الاتصال بقاعدة البيانات
    print(f"🔌 الاتصال بقاعدة البيانات: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ترتيب الجداول حسب التبعيات (Foreign Keys)
        table_order = [
            'categories',
            'users',
            'customers',
            'external_traders',
            'suppliers',
            'products',
            'sales',
            'sale_items',
            'expenses',
            'purchases'
        ]
        
        # حذف البيانات القديمة (بترتيب عكسي لتجنب مشاكل Foreign Keys)
        print("\n🗑️ حذف البيانات القديمة...")
        for table in reversed(table_order):
            if table in data_dict:
                cursor.execute(f"DELETE FROM {table}")
                print(f"   ✓ تم حذف بيانات جدول {table}")
        
        # إعادة تعيين auto_increment
        for table in table_order:
            if table in data_dict:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        conn.commit()
        
        # استيراد البيانات الجديدة
        print("\n📥 استيراد البيانات الجديدة...")
        stats = {}
        
        # مطابقة الأعمدة
        column_mapping = get_table_column_mapping()
        
        for table in table_order:
            if table not in data_dict:
                continue
            
            rows = data_dict[table]
            if not rows:
                continue
            
            # استخدام أعمدة ملف SQL القديم
            if table not in column_mapping:
                print(f"   ⚠️ تخطي جدول {table}: غير موجود في المطابقة")
                continue
                
            columns = column_mapping[table]
            
            # إعداد استعلام INSERT
            placeholders = ','.join(['?' for _ in columns])
            insert_query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            # إدراج البيانات
            imported_count = 0
            for row in rows:
                # تنظيف القيم
                clean_row = [clean_value(val) for val in row]
                
                # التأكد من تطابق عدد الأعمدة
                if len(clean_row) != len(columns):
                    print(f"   ⚠️ تخطي سجل في {table}: عدد الأعمدة غير متطابق (متوقع {len(columns)}، موجود {len(clean_row)})")
                    continue
                
                # تحويل القيم حسب نوع العمود
                final_row = []
                for i, val in enumerate(clean_row):
                    if val is None:
                        final_row.append(None)
                    elif columns[i] in ['id', 'user_id', 'category_id', 'product_id', 
                                        'sale_id', 'supplier_id', 'quantity', 'stock', 
                                        'active', 'is_active']:
                        final_row.append(int(val) if val else 0)
                    elif columns[i] in ['sell_price', 'cost_price', 'total_amount', 
                                        'price_at_sale', 'cost_at_sale', 'total_price',
                                        'amount', 'shop_percentage', 'trader_percentage']:
                        final_row.append(float(val) if val else 0.0)
                    else:
                        final_row.append(val)
                
                try:
                    cursor.execute(insert_query, final_row)
                    imported_count += 1
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطأ في إدراج سجل في {table}: {e}")
                    print(f"      الأعمدة: {columns}")
                    print(f"      البيانات: {final_row}")
            
            conn.commit()
            stats[table] = imported_count
            print(f"   ✓ جدول {table}: تم استيراد {imported_count} سجل")
        
        # عرض الإحصائيات النهائية
        print("\n" + "="*50)
        print("📊 إحصائيات الاستيراد:")
        print("="*50)
        total_records = 0
        for table, count in stats.items():
            print(f"   {table:20} : {count:4} سجل")
            total_records += count
        print("="*50)
        print(f"   إجمالي السجلات المستوردة: {total_records}")
        print("="*50)
        
        print("\n✅ تم استيراد البيانات بنجاح!")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء استيراد البيانات: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def backup_database(db_path):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    if os.path.exists(db_path):
        backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    return None

def main():
    """الوظيفة الرئيسية"""
    # المسارات
    sql_file = r"e:\xamp\htdocs\samir\ni1\back\pos_system.db.sql"
    db_file = r"e:\xamp\htdocs\samir\ni1\pos_system.db"
    
    print("="*60)
    print("       أداة استيراد البيانات - نظام نقاط البيع")
    print("="*60)
    print()
    
    # التحقق من قاعدة البيانات الحالية
    if os.path.exists(db_file):
        response = input("⚠️ قاعدة البيانات موجودة. هل تريد:\n"
                        "  1. إنشاء نسخة احتياطية واستبدال البيانات\n"
                        "  2. الإلغاء\n"
                        "اختر (1 أو 2): ")
        
        if response == '1':
            backup_database(db_file)
            print()
        else:
            print("❌ تم إلغاء العملية")
            return
    else:
        print("ℹ️ قاعدة البيانات غير موجودة - سيتم إنشاؤها من البرنامج")
        print("ℹ️ الرجاء تشغيل البرنامج أولاً لإنشاء الجداول")
        return
    
    # استيراد البيانات
    success = import_data_to_database(sql_file, db_file)
    
    if success:
        print("\n" + "="*60)
        print("✅ العملية اكتملت بنجاح!")
        print("="*60)
        print("\nيمكنك الآن تشغيل البرنامج باستخدام:")
        print("  py -3.8 main.py")
    else:
        print("\n❌ فشلت عملية الاستيراد")

if __name__ == "__main__":
    main()
