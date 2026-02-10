"""
إعدادات التطبيق العامة
"""

# معلومات التطبيق
APP_NAME = "نظام نقاط البيع - سمير لقطع الغيار"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Samir Auto Parts"

# إعدادات قاعدة البيانات
DB_NAME = "pos_system.db"

# إعدادات الواجهة
WINDOW_SIZE = "1200x700"
MIN_WINDOW_SIZE = (1024, 600)

# الألوان (Light Theme)
COLORS = {
    "primary": "#1976d2",
    "primary_dark": "#1565c0",
    "secondary": "#f5f5f5",
    "accent": "#2196f3",
    "info": "#17a2b8",
    "success": "#43a047",
    "warning": "#ffa000",
    "danger": "#e53935",
    "bg": "#ffffff",
    "background": "#ffffff",
    "card_bg": "#f5f5f5",
    "sidebar_bg": "#f0f0f0",
    "surface": "#fafafa",
    "text": "#222222",
    "text_secondary": "#757575",
    "border": "#e0e0e0"
}

# الخطوط
FONTS = {
    "title": ("Arial", 20, "bold"),
    "subtitle": ("Arial", 16, "bold"),
    "heading": ("Arial", 14, "bold"),
    "body": ("Arial", 12),
    "small": ("Arial", 10)
}

# بيانات المستخدم الافتراضية
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123456",
    "full_name": "مدير النظام",
    "role": "admin"
}

# الفئات الافتراضية
DEFAULT_CATEGORIES = [
    "قطع غيار",
    "زيوت ومحركات",
    "إطارات",
    "بطاريات",
    "فلاتر",
    "إكسسوارات",
    "أخرى"
]
