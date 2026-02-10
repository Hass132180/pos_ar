"""
شاشة الإعدادات
"""
import customtkinter as ctk
from config import COLORS, APP_NAME, APP_VERSION
from controllers.auth_controller import AuthController
from ui.components.dialogs import InputDialog, show_error, show_info
from database.connection import db


class SettingsView(ctk.CTkFrame):
    """شاشة الإعدادات"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.create_widgets()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ الإعدادات",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # معلومات النظام
        info_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"🛒 {APP_NAME}",
            font=("Arial", 18, "bold")
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            info_frame,
            text=f"الإصدار: {APP_VERSION}",
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 20))
        
        # المستخدم الحالي
        user_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        user_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            user_frame,
            text="👤 المستخدم الحالي",
            font=("Arial", 16, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            user_frame,
            text=f"الاسم: {self.current_user['full_name']}",
            font=("Arial", 12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            user_frame,
            text=f"اسم المستخدم: {self.current_user['username']}",
            font=("Arial", 12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            user_frame,
            text=f"الصلاحية: {self.current_user['role']}",
            font=("Arial", 12)
        ).pack(pady=(5, 20))
        
        # الإجراءات
        actions_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="🔧 الإجراءات",
            font=("Arial", 16, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkButton(
            actions_frame,
            text="🔑 تغيير كلمة المرور",
            command=self.change_password,
            fg_color=COLORS['primary'],
            height=40,
            width=300
        ).pack(pady=10)
        
        if self.current_user['role'] == 'admin':
            ctk.CTkButton(
                actions_frame,
                text="➕ إضافة مستخدم جديد",
                command=self.add_user,
                fg_color=COLORS['success'],
                height=40,
                width=300
            ).pack(pady=10)
            
            ctk.CTkButton(
                actions_frame,
                text="📊 إحصائيات قاعدة البيانات",
                command=self.show_db_stats,
                fg_color=COLORS['accent'],
                height=40,
                width=300
            ).pack(pady=10)
        
        ctk.CTkButton(
            actions_frame,
            text="ℹ️ عن النظام",
            command=self.show_about,
            fg_color=COLORS['secondary'],
            height=40,
            width=300
        ).pack(pady=(10, 20))
    
    def change_password(self):
        """تغيير كلمة المرور"""
        fields = [
            {'name': 'old_password', 'label': 'كلمة المرور القديمة', 'type': 'entry', 'required': True},
            {'name': 'new_password', 'label': 'كلمة المرور الجديدة', 'type': 'entry', 'required': True},
            {'name': 'confirm_password', 'label': 'تأكيد كلمة المرور', 'type': 'entry', 'required': True}
        ]
        
        dialog = InputDialog(self, "تغيير كلمة المرور", fields)
        result = dialog.get_result()
        
        if result:
            if result['new_password'] != result['confirm_password']:
                show_error("خطأ", "كلمة المرور الجديدة غير متطابقة")
                return
            
            response = AuthController.change_password(
                self.current_user['id'],
                result['old_password'],
                result['new_password']
            )
            
            if response['success']:
                show_info("نجاح", response['message'])
            else:
                show_error("خطأ", response['message'])
    
    def add_user(self):
        """إضافة مستخدم جديد"""
        fields = [
            {'name': 'username', 'label': 'اسم المستخدم', 'type': 'entry', 'required': True},
            {'name': 'password', 'label': 'كلمة المرور', 'type': 'entry', 'required': True},
            {'name': 'full_name', 'label': 'الاسم الكامل', 'type': 'entry', 'required': True},
            {'name': 'role', 'label': 'الصلاحية (admin/cashier)', 'type': 'entry', 'required': True}
        ]
        
        dialog = InputDialog(self, "إضافة مستخدم جديد", fields)
        result = dialog.get_result()
        
        if result:
            response = AuthController.create_user(**result)
            
            if response['success']:
                show_info("نجاح", response['message'])
            else:
                show_error("خطأ", response['message'])
    
    def show_db_stats(self):
        """عرض إحصائيات قاعدة البيانات"""
        stats = []
        
        tables = ['users', 'products', 'customers', 'external_traders', 
                 'sales', 'categories', 'expenses']
        
        for table in tables:
            count = db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            stats.append(f"{table}: {count['count']}")
        
        message = "📊 إحصائيات قاعدة البيانات:\n\n" + "\n".join(stats)
        show_info("إحصائيات", message)
    
    def show_about(self):
        """عن النظام"""
        message = f"""
🛒 {APP_NAME}

الإصدار: {APP_VERSION}

نظام نقاط بيع احترافي وحديث
مبني بلغة Python

الميزات:
✓ نقاط بيع سريعة
✓ إدارة المخزون
✓ إدارة العملاء
✓ إدارة التجار الخارجيين
✓ تقارير مفصلة
✓ واجهة عربية كاملة

© 2025 جميع الحقوق محفوظة
        """
        
        show_info("عن النظام", message.strip())
