"""
الصفحة الرئيسية
"""
import customtkinter as ctk
from config import COLORS, APP_NAME
from controllers.sales_controller import SalesController
from controllers.product_controller import ProductController
from controllers.expense_controller import ExpenseController
from ui.components.cards import StatCard


class HomeView(ctk.CTkFrame):
    """الصفحة الرئيسية"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.create_widgets()
        self.load_stats()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # الترحيب
        welcome_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        welcome_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text=f"مرحباً، {self.current_user['full_name']}! 👋",
            font=("Arial", 28, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text=f"🛒 {APP_NAME}",
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 20))
        
        # إحصائيات سريعة
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 إحصائيات اليوم",
            font=("Arial", 20, "bold")
        ).pack(anchor="e", pady=(0, 10))
        
        # صف الإحصائيات الأول
        stats_row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_row1.pack(fill="x", pady=5)
        stats_row1.grid_columnconfigure((0,1,2), weight=1)
        
        self.sales_count_card = StatCard(stats_row1, "عدد المبيعات", "0", "🛒", COLORS['primary'])
        self.sales_count_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.revenue_card = StatCard(stats_row1, "الإيرادات", "0.00 جنيه", "💰", COLORS['success'])
        self.revenue_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.profit_card = StatCard(stats_row1, "الأرباح", "0.00 جنيه", "📈", COLORS['accent'])
        self.profit_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        # صف الإحصائيات الثاني
        stats_row2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_row2.pack(fill="x", pady=5)
        stats_row2.grid_columnconfigure((0,1,2), weight=1)
        
        self.expenses_card = StatCard(stats_row2, "المصروفات", "0.00 جنيه", "💳", COLORS['danger'])
        self.expenses_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.net_profit_card = StatCard(stats_row2, "صافي الربح", "0.00 جنيه", "💎", COLORS['primary'])
        self.net_profit_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.profit_margin_card = StatCard(stats_row2, "هامش الربح", "0%", "📊", COLORS['accent'])
        self.profit_margin_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        # معلومات المخزون
        inventory_frame = ctk.CTkFrame(self, fg_color="transparent")
        inventory_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            inventory_frame,
            text="📦 معلومات المخزون",
            font=("Arial", 20, "bold")
        ).pack(anchor="e", pady=(0, 10))
        
        inv_row = ctk.CTkFrame(inventory_frame, fg_color="transparent")
        inv_row.pack(fill="x", pady=5)
        inv_row.grid_columnconfigure((0,1,2), weight=1)
        
        self.products_count_card = StatCard(inv_row, "عدد المنتجات", "0", "📦")
        self.products_count_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.inv_value_card = StatCard(inv_row, "قيمة المخزون", "0.00 جنيه", "💰", COLORS['success'])
        self.inv_value_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.low_stock_card = StatCard(inv_row, "منتجات منخفضة", "0", "⚠️", COLORS['warning'])
        self.low_stock_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        # اختصارات سريعة
        shortcuts_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        shortcuts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            shortcuts_frame,
            text="⚡ اختصارات سريعة",
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 10))
        
        buttons_grid = ctk.CTkFrame(shortcuts_frame, fg_color="transparent")
        buttons_grid.pack(pady=20)
        buttons_grid.grid_columnconfigure((0,1,2), weight=1)
        
        shortcuts = [
            ("💰 نقاط البيع", 'pos', COLORS['primary']),
            ("📦 المخزون", 'inventory', COLORS['success']),
            ("👥 العملاء", 'customers', COLORS['accent']),
            ("🤝 التجار", 'traders', COLORS['secondary']),
            ("📊 التقارير", 'reports', COLORS['primary']),
            ("💳 المصروفات", 'expenses', COLORS['danger'])
        ]
        
        for i, (text, view_id, color) in enumerate(shortcuts):
            row = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                buttons_grid,
                text=text,
                command=lambda v=view_id: self.navigate_to(v),
                fg_color=color,
                height=60,
                width=200,
                font=("Arial", 14, "bold")
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
        
        # زر تحديث
        ctk.CTkButton(
            self,
            text="🔄 تحديث الإحصائيات",
            command=self.load_stats,
            fg_color=COLORS['secondary'],
            height=40
        ).pack(pady=10)
    
    def load_stats(self):
        """تحميل الإحصائيات"""
        # مبيعات اليوم
        sales_summary = SalesController.get_sales_summary()
        self.sales_count_card.update_value(sales_summary.get('total_sales', 0) or 0)
        
        total_revenue = sales_summary.get('total_revenue') or 0
        self.revenue_card.update_value(f"{total_revenue:.2f} جنيه")
        
        # الأرباح
        profit_data = SalesController.calculate_profit()
        profit = profit_data.get('profit') or 0
        profit_margin = profit_data.get('profit_margin') or 0
        
        self.profit_card.update_value(f"{profit:.2f} جنيه")
        self.profit_margin_card.update_value(f"{profit_margin:.1f}%")
        
        # المصروفات
        expenses = ExpenseController.get_today_expenses()
        expenses_total = expenses.get('total') or 0
        self.expenses_card.update_value(f"{expenses_total:.2f} جنيه")
        
        # صافي الربح (الربح - المصروفات)
        net_profit = profit - expenses_total
        self.net_profit_card.update_value(f"{net_profit:.2f} جنيه")
        
        # المخزون
        products = ProductController.get_all_products()
        inventory = ProductController.get_total_inventory_value()
        low_stock = ProductController.get_low_stock_products()
        
        self.products_count_card.update_value(len(products))
        self.inv_value_card.update_value(f"{inventory['total_sell']:.2f} جنيه")
        self.low_stock_card.update_value(len(low_stock))
    
    def navigate_to(self, view_id):
        """الانتقال إلى شاشة"""
        # البحث عن الشريط الجانبي والنقر على القائمة
        parent = self.master
        while parent:
            if hasattr(parent, 'handle_menu_click'):
                parent.handle_menu_click(view_id)
                break
            parent = parent.master
