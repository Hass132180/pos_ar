"""
نقطة الدخول الرئيسية للتطبيق
"""
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.migrations import DatabaseMigrations
from ui.main_window import MainWindow


def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل نظام نقاط البيع...")
    
    # تهيئة قاعدة البيانات
    print("📦 تهيئة قاعدة البيانات...")
    migrations = DatabaseMigrations()
    
    if not migrations.initialize():
        print("❌ فشل في تهيئة قاعدة البيانات")
        return
    
    print("✅ تم تهيئة قاعدة البيانات بنجاح")
    
    # إضافة البيانات الافتراضية
    print("📝 إضافة البيانات الافتراضية...")
    if migrations.seed_default_data():
        print("✅ تم إضافة البيانات الافتراضية")
    
    # تشغيل التطبيق
    print("🎨 بدء واجهة المستخدم...")
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
