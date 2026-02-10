"""
شاشة التقارير المتقدمة - نسخة احترافية
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config import COLORS
from controllers.sales_controller import SalesController
from controllers.product_controller import ProductController
from controllers.trader_controller import TraderController
from controllers.expense_controller import ExpenseController
from controllers.purchase_controller import PurchaseController
from ui.components.cards import StatCard
from utils.validators import format_currency


class ReportsView(ctk.CTkFrame):
    """شاشة التقارير المتقدمة"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.current_period = "اليوم"
        
        self.create_widgets()
        self.load_reports()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان واختيار الفترة
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="📊 التقارير والإحصائيات",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # زر التحديث
        refresh_btn = ctk.CTkButton(
            header,
            text="🔄 تحديث",
            command=self.load_reports,
            fg_color=COLORS['success'],
            width=100,
            height=35
        )
        refresh_btn.pack(side="left", padx=5)
        
        # شريط اختيار الفترة الزمنية
        period_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        period_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            period_frame,
            text="📅 الفترة الزمنية:",
            font=("Arial", 14, "bold"),
            text_color=COLORS['text']
        ).pack(side="right", padx=10, pady=10)
        
        # أزرار الفترات
        periods = [
            "اليوم", "هذا الأسبوع", "هذا الشهر", 
            "الشهر الماضي", "آخر 3 شهور", "آخر 6 شهور",
            "هذا العام", "العام الماضي"
        ]
        
        self.period_buttons = {}
        for period in periods:
            btn = ctk.CTkButton(
                period_frame,
                text=period,
                command=lambda p=period: self.change_period(p),
                fg_color="transparent",
                hover_color=COLORS['primary'],
                border_width=2,
                border_color=COLORS['primary'],
                width=120,
                height=35,
                font=("Arial", 11)
            )
            btn.pack(side="right", padx=3, pady=10)
            self.period_buttons[period] = btn
        
        # تحديد الفترة الافتراضية
        self.period_buttons["اليوم"].configure(fg_color=COLORS['primary'])
        
        # إطار التقارير القابل للتمرير
        self.reports_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg']
        )
        self.reports_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ═══════════════════════════════════════
        # 1. الملخص السريع
        # ═══════════════════════════════════════
        summary_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        summary_frame.pack(fill="x", pady=5)
        
        self.period_label = ctk.CTkLabel(
            summary_frame,
            text="📅 ملخص: اليوم",
            font=("Arial", 18, "bold"),
            text_color=COLORS['primary']
        )
        self.period_label.pack(pady=15)
        
        stats_grid = ctk.CTkFrame(summary_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        stats_grid.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        self.sales_count_card = StatCard(stats_grid, "عدد المبيعات", "0", "🛒")
        self.sales_count_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.revenue_card = StatCard(stats_grid, "الإيرادات", "0.00", "💰", COLORS['success'])
        self.revenue_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.expenses_card = StatCard(stats_grid, "المصروفات", "0.00", "💳", COLORS['danger'])
        self.expenses_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.profit_card = StatCard(stats_grid, "صافي الربح", "0.00", "📈", COLORS['primary'])
        self.profit_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        self.margin_card = StatCard(stats_grid, "هامش الربح", "0%", "📊", COLORS['accent'])
        self.margin_card.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        # ═══════════════════════════════════════
        # 2. تقرير المبيعات التفصيلي
        # ═══════════════════════════════════════
        sales_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        sales_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            sales_frame,
            text="� تقرير المبيعات التفصيلي",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        self.sales_text = ctk.CTkTextbox(
            sales_frame,
            font=("Courier New", 11),
            height=200,
            wrap="none"
        )
        self.sales_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        # ═══════════════════════════════════════
        # 3. تقرير المصروفات
        # ═══════════════════════════════════════
        expenses_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        expenses_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            expenses_frame,
            text="💳 تقرير المصروفات",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        self.expenses_text = ctk.CTkTextbox(
            expenses_frame,
            font=("Courier New", 11),
            height=150,
            wrap="none"
        )
        self.expenses_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        # ═══════════════════════════════════════
        # 4. تقرير المشتريات
        # ═══════════════════════════════════════
        purchases_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        purchases_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            purchases_frame,
            text="📥 تقرير المشتريات",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        self.purchases_text = ctk.CTkTextbox(
            purchases_frame,
            font=("Courier New", 11),
            height=150,
            wrap="none"
        )
        self.purchases_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        # ═══════════════════════════════════════
        # 5. تقرير التجار الخارجيين
        # ═══════════════════════════════════════
        traders_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        traders_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            traders_frame,
            text="🤝 تقرير التجار الخارجيين",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        self.traders_text = ctk.CTkTextbox(
            traders_frame,
            font=("Courier New", 11),
            height=200,
            wrap="none"
        )
        self.traders_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        # ═══════════════════════════════════════
        # 6. تقرير المخزون
        # ═══════════════════════════════════════
        inventory_frame = ctk.CTkFrame(self.reports_scroll, fg_color=COLORS['card_bg'])
        inventory_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            inventory_frame,
            text="� تقرير المخزون",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        inv_grid = ctk.CTkFrame(inventory_frame, fg_color="transparent")
        inv_grid.pack(fill="x", padx=20, pady=10)
        inv_grid.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.inv_cost_card = StatCard(inv_grid, "تكلفة المخزون", "0.00", "💵")
        self.inv_cost_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.inv_value_card = StatCard(inv_grid, "قيمة المخزون", "0.00", "💎", COLORS['success'])
        self.inv_value_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.inv_profit_card = StatCard(inv_grid, "الربح المتوقع", "0.00", "🎯", COLORS['primary'])
        self.inv_profit_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.inv_items_card = StatCard(inv_grid, "عدد الأصناف", "0", "📋")
        self.inv_items_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        self.inventory_text = ctk.CTkTextbox(
            inventory_frame,
            font=("Courier New", 11),
            height=200,
            wrap="none"
        )
        self.inventory_text.pack(fill="both", expand=True, padx=15, pady=10)
    
    def change_period(self, period):
        """تغيير الفترة الزمنية"""
        # تحديث لون الأزرار
        for p, btn in self.period_buttons.items():
            if p == period:
                btn.configure(fg_color=COLORS['primary'])
            else:
                btn.configure(fg_color="transparent")
        
        self.current_period = period
        self.period_label.configure(text=f"📅 ملخص: {period}")
        self.load_reports()
    
    def get_date_range(self):
        """الحصول على نطاق التاريخ حسب الفترة المحددة"""
        today = datetime.now()
        
        if self.current_period == "اليوم":
            start_date = today.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "هذا الأسبوع":
            # من الأحد إلى اليوم
            start_of_week = today - timedelta(days=today.weekday() + 1)
            start_date = start_of_week.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "هذا الشهر":
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "الشهر الماضي":
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            start_date = first_day_last_month.strftime("%Y-%m-%d")
            end_date = last_day_last_month.strftime("%Y-%m-%d")
            
        elif self.current_period == "آخر 3 شهور":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "آخر 6 شهور":
            start_date = (today - timedelta(days=180)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "هذا العام":
            start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
        elif self.current_period == "العام الماضي":
            last_year = today.year - 1
            start_date = f"{last_year}-01-01"
            end_date = f"{last_year}-12-31"
        
        else:
            start_date = today.strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        
        return start_date, end_date
    
    def load_reports(self):
        """تحميل جميع التقارير"""
        start_date, end_date = self.get_date_range()
        
        self.load_summary(start_date, end_date)
        self.load_sales_report(start_date, end_date)
        self.load_expenses_report(start_date, end_date)
        self.load_purchases_report(start_date, end_date)
        self.load_traders_report(start_date, end_date)
        self.load_inventory_report()
    
    def load_summary(self, start_date, end_date):
        """تحميل الملخص السريع"""
        from database.connection import db
        
        # عدد المبيعات والإيرادات
        sales_data = db.fetch_one(
            """SELECT COUNT(*) as count, 
                      COALESCE(SUM(total_amount), 0) as revenue
               FROM sales 
               WHERE DATE(created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        
        sales_count = sales_data['count'] or 0
        revenue = sales_data['revenue'] or 0
        
        # حساب الأرباح من sale_items
        profit_data = db.fetch_one(
            """SELECT COALESCE(SUM((si.price_at_sale - si.cost_at_sale) * si.quantity), 0) as profit
               FROM sale_items si
               JOIN sales s ON s.id = si.sale_id
               WHERE DATE(s.created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        
        profit = profit_data['profit'] or 0
        
        # المصروفات
        expenses_data = db.fetch_one(
            """SELECT COALESCE(SUM(amount), 0) as total
               FROM expenses 
               WHERE DATE(created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        
        expenses = expenses_data['total'] or 0
        
        # صافي الربح
        net_profit = profit - expenses
        
        # هامش الربح
        profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        # تحديث البطاقات
        self.sales_count_card.update_value(f"{sales_count}")
        self.revenue_card.update_value(format_currency(revenue))
        self.expenses_card.update_value(format_currency(expenses))
        self.profit_card.update_value(format_currency(net_profit))
        self.margin_card.update_value(f"{profit_margin:.1f}%")
    
    def load_sales_report(self, start_date, end_date):
        """تحميل إحصائيات المبيعات الرقمية فقط"""
        from database.connection import db
        self.sales_text.delete("1.0", "end")
        sales_stats = db.fetch_one(
            """SELECT 
                COUNT(*) as total_sales,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as avg_sale,
                COALESCE(MAX(total_amount), 0) as max_sale,
                COALESCE(MIN(total_amount), 0) as min_sale
               FROM sales 
               WHERE DATE(created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        if not sales_stats or sales_stats['total_sales'] == 0:
            self.sales_text.insert("1.0", "📊 لا توجد مبيعات في هذه الفترة")
            return
        report = "📈 ملخص المبيعات الرقمي\n"
        report += "═" * 40 + "\n\n"
        report += f"🔢 عدد العمليات: {sales_stats['total_sales']}\n"
        report += f"💰 إجمالي الإيرادات: {format_currency(sales_stats['total_revenue'])}\n"
        report += f"📊 متوسط البيع: {format_currency(sales_stats['avg_sale'])}\n"
        report += f"🔝 أكبر عملية: {format_currency(sales_stats['max_sale'])}\n"
        report += f"🔻 أصغر عملية: {format_currency(sales_stats['min_sale'])}\n"
        self.sales_text.insert("1.0", report)
    
    def load_expenses_report(self, start_date, end_date):
        """تحميل إحصائيات المصروفات الرقمية فقط"""
        from database.connection import db
        self.expenses_text.delete("1.0", "end")
        expenses_stats = db.fetch_one(
            """SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(AVG(amount), 0) as avg_expense,
                COALESCE(MAX(amount), 0) as max_expense
               FROM expenses 
               WHERE DATE(created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        if not expenses_stats or expenses_stats['total_count'] == 0:
            self.expenses_text.insert("1.0", "💰 لا توجد مصروفات في هذه الفترة")
            return
        report = "💸 ملخص المصروفات الرقمي\n"
        report += "═" * 40 + "\n\n"
        report += f"🔢 عدد العمليات: {expenses_stats['total_count']}\n"
        report += f"💰 إجمالي المصروفات: {format_currency(expenses_stats['total_amount'])}\n"
        report += f"📊 متوسط المصروف: {format_currency(expenses_stats['avg_expense'])}\n"
        report += f"🔝 أكبر مصروف: {format_currency(expenses_stats['max_expense'])}\n"
        self.expenses_text.insert("1.0", report)
    
    def load_purchases_report(self, start_date, end_date):
        """تحميل إحصائيات المشتريات الرقمية فقط"""
        from database.connection import db
        self.purchases_text.delete("1.0", "end")
        purchases_stats = db.fetch_one(
            """SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(total_amount), 0) as total_amount,
                COALESCE(SUM(quantity), 0) as total_quantity,
                COALESCE(AVG(cost_price), 0) as avg_cost
               FROM purchases 
               WHERE DATE(created_at) BETWEEN ? AND ?""",
            (start_date, end_date)
        )
        if not purchases_stats or purchases_stats['total_count'] == 0:
            self.purchases_text.insert("1.0", "📦 لا توجد مشتريات في هذه الفترة")
            return
        report = "🛒 ملخص المشتريات الرقمي\n"
        report += "═" * 40 + "\n\n"
        report += f"🔢 عدد العمليات: {purchases_stats['total_count']}\n"
        report += f"💰 إجمالي التكلفة: {format_currency(purchases_stats['total_amount'])}\n"
        report += f"📦 إجمالي الكميات: {purchases_stats['total_quantity']}\n"
        report += f"📊 متوسط سعر الشراء: {format_currency(purchases_stats['avg_cost'])}\n"
        self.purchases_text.insert("1.0", report)
    
    def load_traders_report(self, start_date, end_date):
        """تحميل تقرير التجار الخارجيين الرقمي فقط"""
        from database.connection import db
        self.traders_text.delete("1.0", "end")
        traders = db.fetch_all(
            """SELECT et.id, et.name, et.shop_percentage, et.trader_percentage,
                      COUNT(DISTINCT s.id) as sales_count,
                      COALESCE(SUM((si.price_at_sale - si.cost_at_sale) * si.quantity), 0) as total_profit
               FROM external_traders et
               LEFT JOIN products p ON p.external_trader_id = et.id
               LEFT JOIN sale_items si ON si.product_id = p.id
               LEFT JOIN sales s ON s.id = si.sale_id 
                    AND DATE(s.created_at) BETWEEN ? AND ?
               GROUP BY et.id""",
            (start_date, end_date)
        )
        if not traders:
            self.traders_text.insert("1.0", "لا توجد بيانات للتجار")
            return
        total_shop_share = 0
        total_trader_share = 0
        total_profit = 0
        total_sales = 0
        for trader in traders:
            if trader['total_profit'] > 0:
                shop_share = trader['total_profit'] * (trader['shop_percentage'] / 100)
                trader_share = trader['total_profit'] * (trader['trader_percentage'] / 100)
                total_shop_share += shop_share
                total_trader_share += trader_share
                total_profit += trader['total_profit']
                total_sales += trader['sales_count']
        report = "🤝 ملخص أرباح التجار الخارجيين\n"
        report += "═" * 40 + "\n\n"
        report += f"🔢 عدد عمليات البيع: {total_sales}\n"
        report += f"💰 إجمالي أرباح التجار: {format_currency(total_profit)}\n"
        report += f"🏪 إجمالي حصة المحل: {format_currency(total_shop_share)}\n"
        report += f"🧑‍💼 إجمالي حصة التجار: {format_currency(total_trader_share)}\n"
        self.traders_text.insert("1.0", report)
    
    def load_inventory_report(self):
        """تحميل ملخص المخزون الرقمي فقط"""
        self.inventory_text.delete("1.0", "end")
        inventory = ProductController.get_total_inventory_value()
        total_cost = inventory.get('total_cost') or 0
        total_sell = inventory.get('total_sell') or 0
        expected_profit = inventory.get('expected_profit') or 0
        products = ProductController.get_all_products()
        items_count = len(products) if products else 0
        self.inv_cost_card.update_value(format_currency(total_cost))
        self.inv_value_card.update_value(format_currency(total_sell))
        self.inv_profit_card.update_value(format_currency(expected_profit))
        self.inv_items_card.update_value(f"{items_count}")
        report = "📦 ملخص المخزون الرقمي\n"
        report += "═" * 40 + "\n\n"
        report += f"📋 عدد الأصناف: {items_count}\n"
        report += f"💵 التكلفة الإجمالية: {format_currency(total_cost)}\n"
        report += f"💎 القيمة المتوقعة: {format_currency(total_sell)}\n"
        report += f"🎯 الربح المتوقع: {format_currency(expected_profit)}\n"
        self.inventory_text.insert("1.0", report)
