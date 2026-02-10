"""
عرض إدارة المستخدمين
"""
import customtkinter as ctk
from config import COLORS
from controllers.auth_controller import AuthController
from ui.components.dialogs import show_info, show_error, ask_yes_no
from utils.validators import format_currency


class UsersView(ctk.CTkFrame):
    """عرض إدارة المستخدمين"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        
        self.create_ui()
        self.load_users()
    
    def create_ui(self):
        """إنشاء الواجهة"""
        # العنوان
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            header_frame,
            text="👥 إدارة المستخدمين",
            font=("Arial", 24, "bold"),
            text_color=COLORS['text']
        )
        title.pack(side="right")
        
        # زر إضافة مستخدم
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ إضافة مستخدم",
            command=self.show_add_user_dialog,
            fg_color=COLORS['success'],
            hover_color="#27ae60",
            height=35,
            width=150,
            font=("Arial", 12, "bold")
        )
        add_btn.pack(side="left", padx=10)
        
        # إطار المحتوى
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # قائمة المستخدمين
        self.users_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color=COLORS['card_bg']
        )
        self.users_frame.pack(fill="both", expand=True)
    
    def load_users(self):
        """تحميل قائمة المستخدمين"""
        # مسح القائمة
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        users = AuthController.get_all_users()
        
        if not users:
            no_data = ctk.CTkLabel(
                self.users_frame,
                text="لا توجد مستخدمين",
                text_color=COLORS['text_secondary']
            )
            no_data.pack(pady=20)
            return
        
        for user in users:
            self.create_user_card(user)
    
    def create_user_card(self, user):
        """إنشاء بطاقة مستخدم"""
        card = ctk.CTkFrame(self.users_frame, fg_color=COLORS['bg'])
        card.pack(fill="x", pady=10, padx=10)
        
        # معلومات المستخدم
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True, padx=20, pady=15)
        
        # الاسم الكامل
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {user['full_name']}",
            font=("Arial", 14, "bold"),
            text_color=COLORS['text']
        )
        name_label.pack(anchor="e")
        
        # اسم المستخدم والدور
        username_role = f"اسم المستخدم: {user['username']} | الدور: "
        role_text = "مدير النظام" if user['role'] == 'admin' else "بائع"
        role_color = COLORS['primary'] if user['role'] == 'admin' else COLORS['warning']
        
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(anchor="e", pady=5)
        
        ctk.CTkLabel(
            details_frame,
            text=username_role,
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        ).pack(side="right")
        
        ctk.CTkLabel(
            details_frame,
            text=role_text,
            font=("Arial", 11, "bold"),
            text_color=role_color
        ).pack(side="right")
        
        # الحالة
        status_text = "نشط ✓" if user['is_active'] else "معطل ✗"
        status_color = COLORS['success'] if user['is_active'] else COLORS['danger']
        
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"الحالة: {status_text}",
            font=("Arial", 10),
            text_color=status_color
        )
        status_label.pack(anchor="e")
        
        # الأزرار
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.pack(side="left", padx=10)
        
        # زر تعديل كلمة المرور
        password_btn = ctk.CTkButton(
            buttons_frame,
            text="🔑 كلمة المرور",
            width=120,
            command=lambda: self.change_user_password(user),
            fg_color=COLORS['warning'],
            hover_color="#d68910"
        )
        password_btn.pack(side="top", pady=2)
        
        # زر تفعيل/تعطيل
        if user['id'] != self.current_user['id']:  # لا يمكن تعطيل نفسه
            toggle_text = "تعطيل" if user['is_active'] else "تفعيل"
            toggle_color = COLORS['danger'] if user['is_active'] else COLORS['success']
            
            toggle_btn = ctk.CTkButton(
                buttons_frame,
                text=toggle_text,
                width=120,
                command=lambda: self.toggle_user_status(user),
                fg_color=toggle_color,
                hover_color="#c0392b" if user['is_active'] else "#27ae60"
            )
            toggle_btn.pack(side="top", pady=2)
            
            # زر حذف
            if user['username'] != 'admin':  # لا يمكن حذف المدير الأساسي
                delete_btn = ctk.CTkButton(
                    buttons_frame,
                    text="🗑️ حذف",
                    width=120,
                    command=lambda: self.delete_user(user),
                    fg_color=COLORS['danger'],
                    hover_color="#c0392b"
                )
                delete_btn.pack(side="top", pady=2)
    
    def show_add_user_dialog(self):
        """عرض نافذة إضافة مستخدم"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("إضافة مستخدم جديد")
        dialog.geometry("450x500")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # العنوان
        ctk.CTkLabel(
            dialog,
            text="👤 مستخدم جديد",
            font=("Arial", 18, "bold"),
            text_color=COLORS['success']
        ).pack(pady=20)
        
        # اسم المستخدم
        ctk.CTkLabel(
            dialog,
            text="اسم المستخدم:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        username_entry = ctk.CTkEntry(
            dialog,
            width=370,
            height=35,
            placeholder_text="مثال: ahmed",
            font=("Arial", 12)
        )
        username_entry.pack(padx=40, pady=5)
        
        # كلمة المرور
        ctk.CTkLabel(
            dialog,
            text="كلمة المرور:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        password_entry = ctk.CTkEntry(
            dialog,
            width=370,
            height=35,
            placeholder_text="أدخل كلمة المرور",
            show="*",
            font=("Arial", 12)
        )
        password_entry.pack(padx=40, pady=5)
        
        # الاسم الكامل
        ctk.CTkLabel(
            dialog,
            text="الاسم الكامل:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        fullname_entry = ctk.CTkEntry(
            dialog,
            width=370,
            height=35,
            placeholder_text="مثال: أحمد محمد",
            font=("Arial", 12)
        )
        fullname_entry.pack(padx=40, pady=5)
        
        # الدور
        ctk.CTkLabel(
            dialog,
            text="الدور:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        role_var = ctk.StringVar(value="cashier")
        
        role_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        role_frame.pack(padx=40, pady=5)
        
        ctk.CTkRadioButton(
            role_frame,
            text="بائع",
            variable=role_var,
            value="cashier",
            font=("Arial", 12)
        ).pack(side="right", padx=20)
        
        ctk.CTkRadioButton(
            role_frame,
            text="مدير",
            variable=role_var,
            value="admin",
            font=("Arial", 12)
        ).pack(side="right", padx=20)
        
        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            fullname = fullname_entry.get().strip()
            role = role_var.get()
            
            if not username or not password or not fullname:
                show_error("خطأ", "يجب ملء جميع الحقول")
                return
            
            if len(password) < 6:
                show_error("خطأ", "كلمة المرور يجب أن تكون 6 أحرف على الأقل")
                return
            
            result = AuthController.create_user(username, password, fullname, role)
            
            if result['success']:
                show_info("نجاح", result['message'])
                dialog.destroy()
                self.load_users()
            else:
                show_error("خطأ", result['message'])
        
        # أزرار
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="إلغاء",
            command=dialog.destroy,
            fg_color=COLORS['text_secondary'],
            width=170,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="حفظ",
            command=save_user,
            fg_color=COLORS['success'],
            width=170,
            height=40
        ).pack(side="left", padx=5)
    
    def change_user_password(self, user):
        """تغيير كلمة مرور مستخدم"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("تغيير كلمة المرور")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # العنوان
        ctk.CTkLabel(
            dialog,
            text=f"🔑 تغيير كلمة مرور: {user['full_name']}",
            font=("Arial", 16, "bold"),
            text_color=COLORS['warning']
        ).pack(pady=20)
        
        # كلمة المرور الجديدة
        ctk.CTkLabel(
            dialog,
            text="كلمة المرور الجديدة:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        new_password_entry = ctk.CTkEntry(
            dialog,
            width=320,
            height=35,
            placeholder_text="أدخل كلمة المرور الجديدة",
            show="*",
            font=("Arial", 12)
        )
        new_password_entry.pack(padx=40, pady=5)
        new_password_entry.focus()
        
        # تأكيد كلمة المرور
        ctk.CTkLabel(
            dialog,
            text="تأكيد كلمة المرور:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        confirm_password_entry = ctk.CTkEntry(
            dialog,
            width=320,
            height=35,
            placeholder_text="أعد إدخال كلمة المرور",
            show="*",
            font=("Arial", 12)
        )
        confirm_password_entry.pack(padx=40, pady=5)
        
        def save_password():
            new_password = new_password_entry.get().strip()
            confirm_password = confirm_password_entry.get().strip()
            
            if not new_password or not confirm_password:
                show_error("خطأ", "يجب إدخال كلمة المرور")
                return
            
            if len(new_password) < 6:
                show_error("خطأ", "كلمة المرور يجب أن تكون 6 أحرف على الأقل")
                return
            
            if new_password != confirm_password:
                show_error("خطأ", "كلمتا المرور غير متطابقتين")
                return
            
            result = AuthController.change_password(user['id'], "", new_password, is_admin=True)
            
            if result['success']:
                show_info("نجاح", f"تم تغيير كلمة مرور {user['full_name']} بنجاح")
                dialog.destroy()
            else:
                show_error("خطأ", result['message'])
        
        # أزرار
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="إلغاء",
            command=dialog.destroy,
            fg_color=COLORS['text_secondary'],
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="حفظ",
            command=save_password,
            fg_color=COLORS['success'],
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        dialog.bind('<Return>', lambda e: save_password())
    
    def toggle_user_status(self, user):
        """تفعيل/تعطيل مستخدم"""
        action = "تعطيل" if user['is_active'] else "تفعيل"
        
        if ask_yes_no(
            f"{action} المستخدم",
            f"هل تريد {action} المستخدم: {user['full_name']}؟"
        ):
            new_status = 0 if user['is_active'] else 1
            result = AuthController.update_user(user['id'], is_active=new_status)
            
            if result['success']:
                show_info("نجاح", f"تم {action} المستخدم بنجاح")
                self.load_users()
            else:
                show_error("خطأ", result['message'])
    
    def delete_user(self, user):
        """حذف مستخدم"""
        if ask_yes_no(
            "تأكيد الحذف",
            f"هل تريد حذف المستخدم: {user['full_name']}؟\nلا يمكن التراجع عن هذا الإجراء!"
        ):
            result = AuthController.delete_user(user['id'])
            
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_users()
            else:
                show_error("خطأ", result['message'])
