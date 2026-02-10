"""
شاشة المصروفات
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from controllers.expense_controller import ExpenseController
from ui.components.dialogs import InputDialog, show_error, show_info, ask_yes_no
from ui.components.cards import StatCard


class ExpensesView(ctk.CTkFrame):
    """شاشة المصروفات"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان والإحصائيات
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="💳 إدارة المصروفات",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # إحصائيات اليوم
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_frame.grid_columnconfigure((0,1), weight=1)
        
        self.today_count_card = StatCard(stats_frame, "عدد المصروفات اليوم", "0", "📝")
        self.today_count_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.today_total_card = StatCard(stats_frame, "إجمالي المصروفات اليوم", "0.00 جنيه", "💰", COLORS['danger'])
        self.today_total_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        # الأدوات
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            toolbar,
            text="➕ مصروف جديد",
            command=self.add_expense,
            fg_color=COLORS['primary']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="🗑️ حذف",
            command=self.delete_expense,
            fg_color=COLORS['danger']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="🔄 تحديث",
            command=self.load_data
        ).pack(side="left", padx=5)
        
        # الجدول
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("التاريخ", "المبلغ", "الوصف", "الفئة", "المستخدم")
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
        expenses = ExpenseController.get_all_expenses()
        
        self.tree.delete(*self.tree.get_children())
        
        for expense in expenses:
            self.tree.insert(
                "",
                "end",
                values=(
                    expense['created_at'],
                    f"{expense['amount']:.2f}",
                    expense['description'],
                    expense['category'],
                    expense['user_name'] or ""
                ),
                tags=(expense['id'],)
            )
        
        # تحديث الإحصائيات
        today = ExpenseController.get_today_expenses()
        self.today_count_card.update_value(today['count'])
        self.today_total_card.update_value(f"{today['total']:.2f} جنيه")
    
    def add_expense(self):
        """إضافة مصروف"""
        fields = [
            {'name': 'amount', 'label': 'المبلغ', 'type': 'number', 'required': True},
            {'name': 'description', 'label': 'الوصف', 'type': 'text', 'required': True},
            {'name': 'category', 'label': 'الفئة', 'type': 'entry', 'required': False}
        ]
        
        dialog = InputDialog(self, "إضافة مصروف جديد", fields)
        result = dialog.get_result()
        
        if result:
            result['amount'] = float(result.get('amount', 0))
            result['category'] = result.get('category', 'عام')
            
            response = ExpenseController.add_expense(
                user_id=self.current_user['id'],
                **result
            )
            
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def delete_expense(self):
        """حذف مصروف"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار مصروف")
            return
        
        if ask_yes_no("تأكيد", "هل تريد حذف هذا المصروف؟"):
            expense_id = int(self.tree.item(selection[0])['tags'][0])
            result = ExpenseController.delete_expense(expense_id)
            
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_data()
            else:
                show_error("خطأ", result['message'])
