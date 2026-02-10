"""
شاشة تقارير مبيعات المنتجات
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from database.connection import db
from utils.helpers import format_currency
from ui.components.cards import StatCard
from datetime import datetime, timedelta


class ProductSalesView(ctk.CTkFrame):
    """شاشة تقارير المبيعات حسب المنتج"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.current_period = "هذا الشهر"
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان والفترة الزمنية
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="📊 تقارير مبيعات المنتجات",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # اختيار الفترة الزمنية
        period_frame = ctk.CTkFrame(header, fg_color="transparent")
        period_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            period_frame,
            text="الفترة الزمنية:",
            font=("Arial", 12)
        ).pack(side="right", padx=5)
        
        periods = ["اليوم", "هذا الأسبوع", "هذا الشهر", "الشهر الماضي", 
                  "آخر 3 شهور", "آخر 6 شهور", "هذا العام", "العام الماضي", "كل الفترة"]
        
        self.period_combo = ctk.CTkComboBox(
            period_frame,
            values=periods,
            command=self.on_period_change,
            width=150,
            state="readonly"
        )
        self.period_combo.set("هذا الشهر")
        self.period_combo.pack(side="right", padx=5)
        
        # الإحصائيات الرئيسية
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.total_products_card = StatCard(stats_frame, "المنتجات المباعة", "0", "📦")
        self.total_products_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.total_quantity_card = StatCard(stats_frame, "إجمالي القطع", "0", "🔢")
        self.total_quantity_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.total_revenue_card = StatCard(stats_frame, "إجمالي المبيعات", "0.00 جنيه", "💰", COLORS['success'])
        self.total_revenue_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.total_profit_card = StatCard(stats_frame, "إجمالي الأرباح", "0.00 جنيه", "💵", COLORS['primary'])
        self.total_profit_card.grid(row=0, column=3, padx=5, sticky="ew")
        
        # أزرار الترتيب
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            toolbar,
            text="ترتيب حسب:",
            font=("Arial", 12, "bold")
        ).pack(side="right", padx=10)
        
        self.sort_buttons = {}
        
        sort_options = [
            ("quantity", "📦 الأكثر مبيعاً (القطع)"),
            ("revenue", "💰 الأعلى إيراداً"),
            ("profit", "💵 الأكثر ربحاً"),
            ("margin", "📈 أعلى هامش ربح")
        ]
        
        for key, text in sort_options:
            btn = ctk.CTkButton(
                toolbar,
                text=text,
                command=lambda k=key: self.sort_data(k),
                fg_color=COLORS['primary'] if key == 'quantity' else "transparent",
                border_width=2,
                border_color=COLORS['border'],
                width=180
            )
            btn.pack(side="right", padx=5)
            self.sort_buttons[key] = btn
        
        self.current_sort = 'quantity'
        
        # البحث
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 البحث عن منتج...",
            width=300
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_data())
        
        # الجدول
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # إنشاء الجدول مع scrollbar
        columns = ("الترتيب", "المنتج", "الفئة", "القطع المباعة", "الإيرادات", 
                  "التكلفة", "الأرباح", "هامش الربح %")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # تنسيق الأعمدة
        column_widths = [60, 200, 120, 100, 120, 120, 120, 100]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[i], anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="left", fill="y", pady=10)
        
        # تخزين البيانات الكاملة
        self.all_data = []
    
    def get_date_range(self, period):
        """حساب نطاق التاريخ حسب الفترة"""
        end_date = datetime.now()
        
        if period == "اليوم":
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
        elif period == "هذا الأسبوع":
            start_date = end_date - timedelta(days=end_date.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0)
        elif period == "هذا الشهر":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
        elif period == "الشهر الماضي":
            first_day_this_month = end_date.replace(day=1, hour=0, minute=0, second=0)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            start_date = last_day_last_month.replace(day=1, hour=0, minute=0, second=0)
            end_date = last_day_last_month.replace(hour=23, minute=59, second=59)
        elif period == "آخر 3 شهور":
            start_date = end_date - timedelta(days=90)
            start_date = start_date.replace(hour=0, minute=0, second=0)
        elif period == "آخر 6 شهور":
            start_date = end_date - timedelta(days=180)
            start_date = start_date.replace(hour=0, minute=0, second=0)
        elif period == "هذا العام":
            start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0)
        elif period == "العام الماضي":
            start_date = end_date.replace(year=end_date.year-1, month=1, day=1, hour=0, minute=0, second=0)
            end_date = end_date.replace(year=end_date.year-1, month=12, day=31, hour=23, minute=59, second=59)
        else:  # كل الفترة
            return None, None
        
        return start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def on_period_change(self, period):
        """تغيير الفترة الزمنية"""
        self.current_period = period
        self.load_data()
    
    def load_data(self):
        """تحميل بيانات المبيعات حسب المنتج"""
        start_date, end_date = self.get_date_range(self.current_period)
        
        # استعلام SQL لحساب المبيعات حسب المنتج
        if start_date and end_date:
            query = """
                SELECT 
                    p.id,
                    p.name as product_name,
                    c.name as category_name,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.total_price) as total_revenue,
                    SUM(si.quantity * si.cost_at_sale) as total_cost,
                    SUM((si.price_at_sale - si.cost_at_sale) * si.quantity) as total_profit
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                JOIN sales s ON si.sale_id = s.id
                WHERE s.created_at BETWEEN ? AND ?
                GROUP BY p.id, p.name, c.name
                HAVING total_quantity > 0
            """
            raw_data = db.fetch_all(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    p.id,
                    p.name as product_name,
                    c.name as category_name,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.total_price) as total_revenue,
                    SUM(si.quantity * si.cost_at_sale) as total_cost,
                    SUM((si.price_at_sale - si.cost_at_sale) * si.quantity) as total_profit
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                GROUP BY p.id, p.name, c.name
                HAVING total_quantity > 0
            """
            raw_data = db.fetch_all(query)
        
        # تحويل sqlite3.Row إلى قواميس وحساب هامش الربح
        self.all_data = []
        for row in raw_data:
            item = dict(row)
            if item['total_revenue'] > 0:
                item['profit_margin'] = (item['total_profit'] / item['total_revenue']) * 100
            else:
                item['profit_margin'] = 0
            self.all_data.append(item)
        
        # ترتيب البيانات
        self.sort_data(self.current_sort, reload=False)
        
        # تحديث الإحصائيات
        self.update_statistics()
    
    def sort_data(self, sort_by, reload=True):
        """ترتيب البيانات"""
        self.current_sort = sort_by
        
        # تحديث ألوان الأزرار
        for key, btn in self.sort_buttons.items():
            if key == sort_by:
                btn.configure(fg_color=COLORS['primary'])
            else:
                btn.configure(fg_color="transparent")
        
        # ترتيب البيانات
        if sort_by == 'quantity':
            sorted_data = sorted(self.all_data, key=lambda x: x['total_quantity'], reverse=True)
        elif sort_by == 'revenue':
            sorted_data = sorted(self.all_data, key=lambda x: x['total_revenue'], reverse=True)
        elif sort_by == 'profit':
            sorted_data = sorted(self.all_data, key=lambda x: x['total_profit'], reverse=True)
        elif sort_by == 'margin':
            sorted_data = sorted(self.all_data, key=lambda x: x['profit_margin'], reverse=True)
        else:
            sorted_data = self.all_data
        
        # عرض البيانات
        self.display_data(sorted_data)
    
    def filter_data(self):
        """تصفية البيانات حسب البحث"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.sort_data(self.current_sort, reload=False)
            return
        
        filtered_data = [
            item for item in self.all_data
            if search_term in item['product_name'].lower() or 
               (item['category_name'] and search_term in item['category_name'].lower())
        ]
        
        self.display_data(filtered_data)
    
    def display_data(self, data):
        """عرض البيانات في الجدول"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # إضافة البيانات
        for i, item in enumerate(data, 1):
            self.tree.insert(
                "",
                "end",
                values=(
                    i,
                    item['product_name'],
                    item['category_name'] or "غير مصنف",
                    f"{item['total_quantity']:,}",
                    format_currency(item['total_revenue']),
                    format_currency(item['total_cost']),
                    format_currency(item['total_profit']),
                    f"{item['profit_margin']:.1f}%"
                ),
                tags=('profit' if item['total_profit'] > 0 else 'loss',)
            )
        
        # تنسيق الألوان
        self.tree.tag_configure('profit', foreground=COLORS['success'])
        self.tree.tag_configure('loss', foreground=COLORS['danger'])
    
    def update_statistics(self):
        """تحديث البطاقات الإحصائية"""
        if not self.all_data:
            self.total_products_card.update_value("0")
            self.total_quantity_card.update_value("0")
            self.total_revenue_card.update_value("0.00 جنيه")
            self.total_profit_card.update_value("0.00 جنيه")
            return
        
        total_products = len(self.all_data)
        total_quantity = sum(item['total_quantity'] for item in self.all_data)
        total_revenue = sum(item['total_revenue'] for item in self.all_data)
        total_profit = sum(item['total_profit'] for item in self.all_data)
        
        self.total_products_card.update_value(str(total_products))
        self.total_quantity_card.update_value(f"{total_quantity:,}")
        self.total_revenue_card.update_value(format_currency(total_revenue))
        self.total_profit_card.update_value(format_currency(total_profit))
