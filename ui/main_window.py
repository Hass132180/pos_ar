"""
النافذة الرئيسية للتطبيق
"""
import customtkinter as ctk
from ui.themes import AppTheme
from ui.components.sidebar import Sidebar
from ui.components.dialogs import show_error, ask_yes_no
from config import APP_NAME, WINDOW_SIZE, MIN_WINDOW_SIZE, COLORS
from controllers.auth_controller import AuthController


class MainWindow(ctk.CTk):
    """النافذة الرئيسية"""
    
    def __init__(self):
        super().__init__()
        
        # إعداد النافذة
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        
        # إعداد الثيم
        AppTheme.setup()
        
        # المتغيرات
        self.current_user = None
        self.current_view = None
        self.sidebar = None
        self.content_frame = None
        
        # عرض شاشة تسجيل الدخول
        self.show_login()
    
    def show_login(self):
        """عرض شاشة تسجيل الدخول"""
        # مسح المحتوى
        for widget in self.winfo_children():
            widget.destroy()
        
        # إطار تسجيل الدخول
        login_frame = ctk.CTkFrame(self, fg_color=COLORS['bg'])
        login_frame.pack(fill="both", expand=True)
        
        # بطاقة تسجيل الدخول
        card = ctk.CTkFrame(login_frame, fg_color=COLORS['card_bg'], corner_radius=15, width=400, height=500)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # الشعار والعنوان
        logo_label = ctk.CTkLabel(
            card,
            text="🛒",
            font=("Arial", 48)
        )
        logo_label.pack(pady=(40, 10))
        
        title_label = ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=("Arial", 24, "bold"),
            text_color=COLORS['primary']
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            card,
            text="نظام نقاط البيع الحديث",
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 40))
        
        # حقل اسم المستخدم
        username_label = ctk.CTkLabel(
            card,
            text="اسم المستخدم",
            font=("Arial", 12),
            text_color=COLORS['text']
        )
        username_label.pack(anchor="e", padx=40, pady=(0, 5))
        
        username_entry = ctk.CTkEntry(
            card,
            placeholder_text="أدخل اسم المستخدم",
            height=40,
            font=("Arial", 12)
        )
        username_entry.pack(fill="x", padx=40, pady=(0, 20))
        
        # حقل كلمة المرور
        password_label = ctk.CTkLabel(
            card,
            text="كلمة المرور",
            font=("Arial", 12),
            text_color=COLORS['text']
        )
        password_label.pack(anchor="e", padx=40, pady=(0, 5))
        
        password_entry = ctk.CTkEntry(
            card,
            placeholder_text="أدخل كلمة المرور",
            show="*",
            height=40,
            font=("Arial", 12)
        )
        password_entry.pack(fill="x", padx=40, pady=(0, 30))
        
        # زر تسجيل الدخول
        login_btn = ctk.CTkButton(
            card,
            text="تسجيل الدخول",
            command=lambda: self.do_login(username_entry.get(), password_entry.get()),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            font=("Arial", 14, "bold")
        )
        login_btn.pack(fill="x", padx=40, pady=(0, 20))
        
        # Enter للتسجيل
        password_entry.bind('<Return>', lambda e: self.do_login(username_entry.get(), password_entry.get()))
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        
        # تركيز على حقل اسم المستخدم
        username_entry.focus()
    
    def do_login(self, username, password):
        """تنفيذ تسجيل الدخول"""
        if not username or not password:
            show_error("خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        result = AuthController.login(username, password)
        
        if result['success']:
            self.current_user = result['user']
            self.show_main_interface()
        else:
            show_error("خطأ في تسجيل الدخول", result['message'])
    
    def show_main_interface(self):
        """عرض الواجهة الرئيسية بعد تسجيل الدخول"""
        # مسح المحتوى
        for widget in self.winfo_children():
            widget.destroy()
        
        # الإطار الرئيسي
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg'])
        main_frame.pack(fill="both", expand=True)
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # الشريط الجانبي - مع تمرير بيانات المستخدم
        self.sidebar = Sidebar(main_frame, self.handle_menu_click, self.current_user)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # منطقة المحتوى
        self.content_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg'])
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # عرض الصفحة المناسبة حسب الدور
        # البائع يذهب مباشرة لنقاط البيع، المدير للصفحة الرئيسية
        if self.current_user.get('role') == 'cashier':
            self.handle_menu_click('pos')
        else:
            self.handle_menu_click('home')
    
    def handle_menu_click(self, view_id):
        """معالجة النقر على قائمة التنقل"""
        if view_id == 'logout':
            if ask_yes_no("تسجيل الخروج", "هل أنت متأكد من تسجيل الخروج؟"):
                self.logout()
            return
        
        # التحقق من الصلاحيات - الصفحات المحمية للمدير فقط
        is_admin = self.current_user.get('role') == 'admin'
        protected_views = ['inventory', 'customers', 'traders', 'reports', 'product_sales', 'expenses', 'purchases', 'users', 'settings']
        
        if not is_admin and view_id in protected_views:
            show_error("غير مصرح", "ليس لديك صلاحية للوصول إلى هذه الصفحة")
            return
        
        # مسح المحتوى السابق
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # عرض الشاشة المطلوبة
        if view_id == 'home':
            self.show_home()
        elif view_id == 'pos':
            self.show_pos()
        elif view_id == 'inventory':
            self.show_inventory()
        elif view_id == 'customers':
            self.show_customers()
        elif view_id == 'traders':
            self.show_traders()
        elif view_id == 'reports':
            self.show_reports()
        elif view_id == 'product_sales':
            self.show_product_sales()
        elif view_id == 'expenses':
            self.show_expenses()
        elif view_id == 'purchases':
            self.show_purchases()
        elif view_id == 'users':
            self.show_users()
        elif view_id == 'settings':
            self.show_settings()

    
    def show_home(self):
        """عرض الصفحة الرئيسية"""
        from views.home_view import HomeView
        view = HomeView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_pos(self):
        """عرض نقاط البيع"""
        from views.pos_view import POSView
        view = POSView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_inventory(self):
        """عرض المخزون"""
        from views.inventory_view import InventoryView
        view = InventoryView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_customers(self):
        """عرض العملاء"""
        from views.customers_view import CustomersView
        view = CustomersView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_traders(self):
        """عرض التجار الخارجيين"""
        from views.traders_view import TradersView
        view = TradersView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_reports(self):
        """عرض التقارير"""
        from views.reports_view import ReportsView
        view = ReportsView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_product_sales(self):
        """عرض تقارير مبيعات المنتجات"""
        from views.product_sales_view import ProductSalesView
        view = ProductSalesView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_expenses(self):
        """عرض المصروفات"""
        from views.expenses_view import ExpensesView
        view = ExpensesView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_purchases(self):
        """عرض المشتريات"""
        from views.purchases_view import PurchasesView
        view = PurchasesView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_users(self):
        """عرض إدارة المستخدمين"""
        from views.users_view import UsersView
        view = UsersView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    
    def show_settings(self):
        """عرض الإعدادات"""
        from views.settings_view import SettingsView
        view = SettingsView(self.content_frame, self.current_user)
        view.pack(fill="both", expand=True)
    

    
    def logout(self):
        """تسجيل الخروج"""
        self.current_user = None
        self.show_login()
