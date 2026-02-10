"""
شاشة إدارة التجار الخارجيين
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from controllers.trader_controller import TraderController
from ui.components.dialogs import InputDialog, show_error, show_info, ask_yes_no
from ui.components.cards import StatCard


class TradersView(ctk.CTkFrame):
    """شاشة التجار الخارجيين"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="🤝 التجار الخارجيين",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # الأدوات
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="البحث...",
            width=300
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.load_data())
        
        ctk.CTkButton(
            toolbar,
            text="➕ تاجر جديد",
            command=self.add_trader,
            fg_color=COLORS['primary']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="✏️ تعديل",
            command=self.edit_trader
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="📊 تقرير الأرباح",
            command=self.show_report,
            fg_color=COLORS['success']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="🗑️ حذف",
            command=self.delete_trader,
            fg_color=COLORS['danger']
        ).pack(side="left", padx=5)
        
        # الجدول
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("الاسم", "الهاتف", "نسبة المحل%", "نسبة التاجر%", "تاريخ الإضافة")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="left", fill="y", pady=10)
    
    def load_data(self):
        """تحميل البيانات"""
        query = self.search_entry.get().strip()
        traders = TraderController.get_all_traders(query)
        
        self.tree.delete(*self.tree.get_children())
        
        for trader in traders:
            self.tree.insert(
                "",
                "end",
                values=(
                    trader['name'],
                    trader['phone'] or "",
                    f"{trader['shop_percentage']:.1f}",
                    f"{trader['trader_percentage']:.1f}",
                    trader['created_at']
                ),
                tags=(trader['id'],)
            )
    
    def add_trader(self):
        """إضافة تاجر"""
        fields = [
            {'name': 'name', 'label': 'الاسم', 'type': 'entry', 'required': True},
            {'name': 'phone', 'label': 'الهاتف', 'type': 'entry', 'required': False},
            {'name': 'address', 'label': 'العنوان', 'type': 'entry', 'required': False},
            {'name': 'email', 'label': 'البريد الإلكتروني', 'type': 'entry', 'required': False},
            {'name': 'shop_percentage', 'label': 'نسبة المحل %', 'type': 'number', 'required': True},
            {'name': 'notes', 'label': 'ملاحظات', 'type': 'text', 'required': False}
        ]
        
        dialog = InputDialog(self, "إضافة تاجر جديد", fields)
        result = dialog.get_result()
        
        if result:
            result['shop_percentage'] = float(result.get('shop_percentage', 20))
            response = TraderController.add_trader(**result)
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def edit_trader(self):
        """تعديل تاجر"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار تاجر")
            return
        
        show_info("قريباً", "سيتم إضافة التعديل قريباً")
    
    def show_report(self):
        """عرض تقرير الأرباح"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار تاجر")
            return
        
        trader_id = int(self.tree.item(selection[0])['tags'][0])
        profits = TraderController.calculate_trader_profits(trader_id)
        
        if profits:
            message = (
                f"تاجر: {profits['trader_name']}\n\n"
                f"عدد المبيعات: {profits['total_sales']}\n"
                f"إجمالي الربح: {profits['total_profit']:.2f} جنيه\n\n"
                f"حصة المحل ({profits['shop_percentage']:.1f}%): {profits['shop_share']:.2f} جنيه\n"
                f"حصة التاجر ({profits['trader_percentage']:.1f}%): {profits['trader_share']:.2f} جنيه"
            )
            show_info("تقرير أرباح التاجر", message)
        else:
            show_error("خطأ", "لم يتم العثور على بيانات")
    
    def delete_trader(self):
        """حذف تاجر"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار تاجر")
            return
        
        if ask_yes_no("تأكيد", "هل تريد حذف هذا التاجر؟"):
            trader_id = int(self.tree.item(selection[0])['tags'][0])
            result = TraderController.delete_trader(trader_id)
            
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_data()
            else:
                show_error("خطأ", result['message'])
