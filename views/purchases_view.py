"""
عرض المشتريات
"""
import customtkinter as ctk
from config import COLORS
from controllers.purchase_controller import PurchaseController
from controllers.product_controller import ProductController
from ui.components.dialogs import show_info, show_error, ask_yes_no
from utils.validators import format_currency


class PurchasesView(ctk.CTkFrame):
    """عرض المشتريات"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.selected_product_id = None
        self.selected_supplier_id = None
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """إنشاء الواجهة"""
        # العنوان
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            header_frame,
            text="📥 المشتريات",
            font=("Arial", 24, "bold"),
            text_color=COLORS['text']
        )
        title.pack(side="right")
        
        # إحصائيات سريعة
        stats_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.today_label = ctk.CTkLabel(
            stats_frame,
            text="مشتريات اليوم: 0.00 جنيه",
            font=("Arial", 14),
            text_color=COLORS['text']
        )
        self.today_label.pack(pady=10)
        
        # إطار المحتوى الرئيسي
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # إطار الإضافة (يسار)
        add_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['card_bg'], width=350)
        add_frame.pack(side="right", fill="y", padx=(0, 10))
        add_frame.pack_propagate(False)
        
        add_title = ctk.CTkLabel(
            add_frame,
            text="إضافة مشترى جديد",
            font=("Arial", 16, "bold"),
            text_color=COLORS['primary']
        )
        add_title.pack(pady=15)
        
        # اختيار المنتج
        ctk.CTkLabel(add_frame, text="اختر المنتج:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        self.product_combo = ctk.CTkComboBox(
            add_frame,
            values=["جاري التحميل..."],
            width=310,
            state="readonly"
        )
        self.product_combo.pack(padx=20, pady=5)
        
        # اختيار المورد
        ctk.CTkLabel(add_frame, text="اختر المورد (اختياري):", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        supplier_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        supplier_frame.pack(padx=20, pady=5)
        
        self.supplier_combo = ctk.CTkComboBox(
            supplier_frame,
            values=["جاري التحميل..."],
            width=230,
            state="readonly"
        )
        self.supplier_combo.pack(side="right", padx=(10, 0))
        
        add_supplier_btn = ctk.CTkButton(
            supplier_frame,
            text="+",
            width=50,
            command=self.show_add_supplier_dialog,
            fg_color=COLORS['success']
        )
        add_supplier_btn.pack(side="right")
        
        # الكمية
        ctk.CTkLabel(add_frame, text="الكمية:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        self.quantity_entry = ctk.CTkEntry(add_frame, width=310, placeholder_text="مثال: 50")
        self.quantity_entry.pack(padx=20, pady=5)
        
        # سعر الشراء
        ctk.CTkLabel(add_frame, text="سعر الشراء (للوحدة):", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        self.cost_entry = ctk.CTkEntry(add_frame, width=310, placeholder_text="مثال: 25.00")
        self.cost_entry.pack(padx=20, pady=5)
        
        # رقم الفاتورة
        ctk.CTkLabel(add_frame, text="رقم الفاتورة (اختياري):", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        self.invoice_entry = ctk.CTkEntry(add_frame, width=310)
        self.invoice_entry.pack(padx=20, pady=5)
        
        # ملاحظات
        ctk.CTkLabel(add_frame, text="ملاحظات (اختياري):", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        
        self.notes_entry = ctk.CTkEntry(add_frame, width=310)
        self.notes_entry.pack(padx=20, pady=5)
        
        # زر الإضافة
        add_btn = ctk.CTkButton(
            add_frame,
            text="إضافة المشترى",
            command=self.add_purchase,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            height=40,
            width=310,
            font=("Arial", 14, "bold")
        )
        add_btn.pack(pady=20)
        
        # قائمة المشتريات (يمين)
        list_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['card_bg'])
        list_frame.pack(side="right", fill="both", expand=True)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="سجل المشتريات",
            font=("Arial", 16, "bold"),
            text_color=COLORS['text']
        )
        list_title.pack(pady=15)
        
        # جدول المشتريات
        self.purchases_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=COLORS['bg']
        )
        self.purchases_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self):
        """تحميل البيانات"""
        # تحميل المنتجات
        products = ProductController.get_all_products()
        if products:
            product_names = [f"{p['name']} (المخزون: {p['stock']})" for p in products]
            self.product_combo.configure(values=product_names)
            self.product_combo.set(product_names[0] if product_names else "")
            self.products_data = products
        
        # تحميل الموردين
        suppliers = PurchaseController.get_suppliers()
        supplier_names = ["بدون مورد"] + [s['name'] for s in suppliers]
        self.supplier_combo.configure(values=supplier_names)
        self.supplier_combo.set("بدون مورد")
        self.suppliers_data = suppliers
        
        # تحديث الإحصائيات
        self.update_stats()
        
        # تحميل المشتريات
        self.load_purchases()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        today = PurchaseController.get_today_purchases()
        self.today_label.configure(
            text=f"مشتريات اليوم: {format_currency(today['total'])} ({today['count']} عملية)"
        )
    
    def load_purchases(self):
        """تحميل قائمة المشتريات"""
        # مسح القائمة
        for widget in self.purchases_frame.winfo_children():
            widget.destroy()
        
        purchases = PurchaseController.get_all_purchases(limit=50)
        
        if not purchases:
            no_data = ctk.CTkLabel(
                self.purchases_frame,
                text="لا توجد مشتريات",
                text_color=COLORS['text_secondary']
            )
            no_data.pack(pady=20)
            return
        
        for purchase in purchases:
            self.create_purchase_item(purchase)
    
    def create_purchase_item(self, purchase):
        """إنشاء عنصر مشترى"""
        item_frame = ctk.CTkFrame(self.purchases_frame, fg_color=COLORS['card_bg'])
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # المعلومات
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True, padx=10, pady=10)
        
        # السطر الأول: المنتج والمورد
        row1 = ctk.CTkLabel(
            info_frame,
            text=f"المنتج: {purchase['product_name']} | المورد: {purchase['supplier_name'] or 'غير محدد'}",
            font=("Arial", 12, "bold"),
            text_color=COLORS['text']
        )
        row1.pack(anchor="e")
        
        # السطر الثاني: الكمية والسعر
        row2 = ctk.CTkLabel(
            info_frame,
            text=f"الكمية: {purchase['quantity']} | سعر الشراء: {format_currency(purchase['cost_price'])} | الإجمالي: {format_currency(purchase['total_amount'])}",
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        )
        row2.pack(anchor="e")
        
        # السطر الثالث: التاريخ
        row3 = ctk.CTkLabel(
            info_frame,
            text=f"التاريخ: {purchase['created_at']}",
            font=("Arial", 10),
            text_color=COLORS['text_secondary']
        )
        row3.pack(anchor="e")
        
        # زر الحذف
        delete_btn = ctk.CTkButton(
            item_frame,
            text="حذف",
            width=60,
            command=lambda: self.delete_purchase(purchase['id']),
            fg_color=COLORS['danger'],
            hover_color="#c0392b"
        )
        delete_btn.pack(side="left", padx=10)
    
    def add_purchase(self):
        """إضافة مشترى"""
        # التحقق من المنتج
        if not hasattr(self, 'products_data') or not self.products_data:
            show_error("خطأ", "لا توجد منتجات")
            return
        
        product_index = self.product_combo.cget("values").index(self.product_combo.get())
        product_id = self.products_data[product_index]['id']
        
        # التحقق من المورد
        supplier_id = None
        if self.supplier_combo.get() != "بدون مورد":
            supplier_index = self.supplier_combo.cget("values").index(self.supplier_combo.get()) - 1
            supplier_id = self.suppliers_data[supplier_index]['id']
        
        # التحقق من الكمية
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                show_error("خطأ", "الكمية يجب أن تكون أكبر من صفر")
                return
        except ValueError:
            show_error("خطأ", "الكمية غير صحيحة")
            return
        
        # التحقق من السعر
        try:
            cost_price = float(self.cost_entry.get())
            if cost_price <= 0:
                show_error("خطأ", "السعر يجب أن يكون أكبر من صفر")
                return
        except ValueError:
            show_error("خطأ", "السعر غير صحيح")
            return
        
        invoice = self.invoice_entry.get()
        notes = self.notes_entry.get()
        
        # إضافة المشترى
        result = PurchaseController.add_purchase(
            product_id, quantity, cost_price, supplier_id, invoice, notes
        )
        
        if result['success']:
            show_info("نجاح", result['message'])
            self.clear_form()
            self.load_data()
        else:
            show_error("خطأ", result['message'])
    
    def delete_purchase(self, purchase_id):
        """حذف مشترى"""
        if ask_yes_no("تأكيد الحذف", "هل تريد حذف هذا المشترى؟"):
            result = PurchaseController.delete_purchase(purchase_id)
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_data()
            else:
                show_error("خطأ", result['message'])
    
    def show_add_supplier_dialog(self):
        """عرض نافذة إضافة مورد"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("إضافة مورد جديد")
        dialog.geometry("450x380")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # تركيز النافذة في المنتصف
        dialog.after(100, lambda: dialog.focus())
        
        # اسم المورد
        ctk.CTkLabel(dialog, text="اسم المورد:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=360)
        name_entry.pack(padx=20, pady=5)
        
        # الهاتف
        ctk.CTkLabel(dialog, text="الهاتف:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        phone_entry = ctk.CTkEntry(dialog, width=360)
        phone_entry.pack(padx=20, pady=5)
        
        # الشركة
        ctk.CTkLabel(dialog, text="الشركة:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        company_entry = ctk.CTkEntry(dialog, width=360)
        company_entry.pack(padx=20, pady=5)
        
        # العنوان
        ctk.CTkLabel(dialog, text="العنوان:", 
                    text_color=COLORS['text']).pack(anchor="e", padx=20, pady=(10, 5))
        address_entry = ctk.CTkEntry(dialog, width=360)
        address_entry.pack(padx=20, pady=5)
        
        def save_supplier():
            name = name_entry.get().strip()
            if not name:
                show_error("خطأ", "يجب إدخال اسم المورد")
                return
            
            result = PurchaseController.add_supplier(
                name, 
                phone_entry.get().strip(), 
                company_entry.get().strip(), 
                address_entry.get().strip()
            )
            
            if result['success']:
                show_info("نجاح", result['message'])
                dialog.destroy()
                self.load_data()
            else:
                show_error("خطأ", result['message'])
        
        def cancel():
            dialog.destroy()
        
        # ربط مفتاح Enter بجميع الحقول
        name_entry.bind("<Return>", lambda e: save_supplier())
        phone_entry.bind("<Return>", lambda e: save_supplier())
        company_entry.bind("<Return>", lambda e: save_supplier())
        address_entry.bind("<Return>", lambda e: save_supplier())
        
        # تركيز على الحقل الأول
        name_entry.focus()
        
        # إطار الأزرار
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        # زر الإلغاء
        ctk.CTkButton(
            buttons_frame,
            text="إلغاء",
            command=cancel,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS['border'],
            width=170,
            height=40
        ).pack(side="left", padx=5)
        
        # زر الحفظ
        ctk.CTkButton(
            buttons_frame,
            text="✅ حفظ المورد",
            command=save_supplier,
            fg_color=COLORS['success'],
            width=170,
            height=40
        ).pack(side="right", padx=5)
    
    def clear_form(self):
        """مسح النموذج"""
        self.quantity_entry.delete(0, 'end')
        self.cost_entry.delete(0, 'end')
        self.invoice_entry.delete(0, 'end')
        self.notes_entry.delete(0, 'end')
