"""
شاشة إدارة العملاء
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from controllers.customer_controller import CustomerController
from ui.components.dialogs import InputDialog, show_error, show_info, ask_yes_no


class CustomersView(ctk.CTkFrame):
    """شاشة العملاء"""
    
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
            text="👥 إدارة العملاء",
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
            text="➕ عميل جديد",
            command=self.add_customer,
            fg_color=COLORS['primary']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="✏️ تعديل",
            command=self.edit_customer
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="🗑️ حذف",
            command=self.delete_customer,
            fg_color=COLORS['danger']
        ).pack(side="left", padx=5)
        
        # الجدول
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("الاسم", "الهاتف", "العنوان", "البريد الإلكتروني", "تاريخ الإضافة")
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
        customers = CustomerController.get_all_customers(query)
        
        self.tree.delete(*self.tree.get_children())
        
        for customer in customers:
            self.tree.insert(
                "",
                "end",
                values=(
                    customer['name'],
                    customer['phone'] or "",
                    customer['address'] or "",
                    customer['email'] or "",
                    customer['created_at']
                ),
                tags=(customer['id'],)
            )
    
    def add_customer(self):
        """إضافة عميل"""
        fields = [
            {'name': 'name', 'label': 'الاسم', 'type': 'entry', 'required': True},
            {'name': 'phone', 'label': 'الهاتف', 'type': 'entry', 'required': False},
            {'name': 'address', 'label': 'العنوان', 'type': 'entry', 'required': False},
            {'name': 'email', 'label': 'البريد الإلكتروني', 'type': 'entry', 'required': False},
            {'name': 'notes', 'label': 'ملاحظات', 'type': 'text', 'required': False}
        ]
        
        dialog = InputDialog(self, "إضافة عميل جديد", fields)
        result = dialog.get_result()
        
        if result:
            response = CustomerController.add_customer(**result)
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def edit_customer(self):
        """تعديل عميل"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار عميل")
            return
        
        customer_id = int(self.tree.item(selection[0])['tags'][0])
        customer = CustomerController.get_customer_by_id(customer_id)
        
        # سيتم تحسينه لاحقاً مع القيم الافتراضية
        show_info("قريباً", "سيتم إضافة التعديل قريباً")
    
    def delete_customer(self):
        """حذف عميل"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار عميل")
            return
        
        if ask_yes_no("تأكيد", "هل تريد حذف هذا العميل؟"):
            customer_id = int(self.tree.item(selection[0])['tags'][0])
            result = CustomerController.delete_customer(customer_id)
            
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_data()
            else:
                show_error("خطأ", result['message'])
