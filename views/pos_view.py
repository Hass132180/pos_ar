"""
شاشة نقاط البيع (POS)
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from controllers.product_controller import ProductController
from controllers.sales_controller import SalesController
from controllers.customer_controller import CustomerController
from controllers.expense_controller import ExpenseController
from ui.components.dialogs import show_error, show_info, ask_yes_no, InputDialog, SimpleInputDialog
from utils.validators import validate_number, format_currency


class POSView(ctk.CTkFrame):
    """شاشة نقاط البيع"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.cart_items = []
        self.customers = []
        
        self.create_widgets()
        self.load_customers()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # تقسيم الشاشة إلى جزئين
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # الجزء الأيسر - البحث والمنتجات
        left_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        
        # العنوان والإحصائيات
        header_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            header_frame,
            text="💰 نقاط البيع",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # زر المصاريف السريع
        quick_expense_btn = ctk.CTkButton(
            header_frame,
            text="💸 مصروف سريع",
            command=self.add_quick_expense,
            fg_color=COLORS['warning'],
            hover_color="#d68910",
            height=35,
            width=120,
            font=("Arial", 12, "bold")
        )
        quick_expense_btn.pack(side="left", padx=5)
        
        # زر المرتجعات
        returns_btn = ctk.CTkButton(
            header_frame,
            text="↩️ مرتجعات",
            command=self.open_returns_dialog,
            fg_color=COLORS['danger'],
            height=35,
            width=120,
            font=("Arial", 12, "bold")
        )
        returns_btn.pack(side="left", padx=5)
        
        # إحصائيات اليوم
        stats_frame = ctk.CTkFrame(left_frame, fg_color=COLORS['bg'])
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # مبيعات اليوم
        self.sales_label = ctk.CTkLabel(
            stats_frame,
            text="مبيعات اليوم: 0.00 ج",
            font=("Arial", 12, "bold"),
            text_color=COLORS['success']
        )
        self.sales_label.pack(side="right", padx=10)
        
        # مصاريف اليوم
        self.expenses_label = ctk.CTkLabel(
            stats_frame,
            text="مصاريف اليوم: 0.00 ج",
            font=("Arial", 12, "bold"),
            text_color=COLORS['danger']
        )
        self.expenses_label.pack(side="right", padx=10)
        
        # المبلغ في الدرج
        self.drawer_label = ctk.CTkLabel(
            stats_frame,
            text="في الدرج: 0.00 ج",
            font=("Arial", 12, "bold"),
            text_color=COLORS['primary']
        )
        self.drawer_label.pack(side="right", padx=10)
        
        # تحديث الإحصائيات
        self.update_daily_stats()
        
        # البحث والتصفية
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # إطار البحث الأول
        search_row1 = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_row1.pack(fill="x", pady=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_row1,
            placeholder_text="ابحث بالاسم أو الباركود...",
            height=40,
            font=("Arial", 12)
        )
        self.search_entry.pack(side="right", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_products())
        self.search_entry.bind('<Return>', lambda e: self.add_first_product())
        
        search_btn = ctk.CTkButton(
            search_row1,
            text="🔍",
            width=40,
            command=self.search_products
        )
        search_btn.pack(side="right")
        
        # إطار التصفية بالقسم
        filter_row = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_row.pack(fill="x")
        
        ctk.CTkLabel(
            filter_row,
            text="القسم:",
            font=("Arial", 12)
        ).pack(side="right", padx=(0, 5))
        
        self.category_var = ctk.StringVar(value="جميع الأقسام")
        self.category_combo = ctk.CTkComboBox(
            filter_row,
            variable=self.category_var,
            values=["جميع الأقسام"],
            width=200,
            command=self.on_category_changed
        )
        self.category_combo.pack(side="right")
        
        # قائمة المنتجات
        products_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        products_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview للمنتجات
        columns = ("الاسم", "السعر", "المخزون", "الباركود")
        self.products_tree = ttk.Treeview(
            products_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(
            products_frame,
            orient="vertical",
            command=self.products_tree.yview
        )
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        self.products_tree.bind('<Double-1>', lambda e: self.add_to_cart())
        
        # الجزء الأيمن - السلة والدفع
        right_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        
        # العنوان
        cart_title = ctk.CTkLabel(
            right_frame,
            text="🛒 سلة المشتريات",
            font=("Arial", 18, "bold")
        )
        cart_title.pack(pady=20)
        
        # اختيار العميل
        customer_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            customer_frame,
            text="العميل:",
            font=("Arial", 12)
        ).pack(side="right", padx=5)
        
        self.customer_var = ctk.StringVar(value="بدون عميل")
        self.customer_combo = ctk.CTkComboBox(
            customer_frame,
            variable=self.customer_var,
            values=["بدون عميل"],
            width=200
        )
        self.customer_combo.pack(side="right")
        
        # قائمة السلة
        cart_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        cart_columns = ("المنتج", "الكمية", "السعر", "الإجمالي")
        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=cart_columns,
            show="headings",
            height=10
        )
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100, anchor="center")
        
        cart_scroll = ttk.Scrollbar(
            cart_frame,
            orient="vertical",
            command=self.cart_tree.yview
        )
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)
        
        self.cart_tree.pack(side="right", fill="both", expand=True)
        cart_scroll.pack(side="left", fill="y")
        
        # أزرار التحكم في السلة
        cart_btns = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_btns.pack(fill="x", padx=20, pady=5)
        
        # الصف الأول من الأزرار
        cart_btns_row1 = ctk.CTkFrame(cart_btns, fg_color="transparent")
        cart_btns_row1.pack(fill="x", pady=(0, 2))
        
        ctk.CTkButton(
            cart_btns_row1,
            text="✏️ كمية",
            command=self.edit_quantity,
            fg_color=COLORS['info'],
            width=70
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            cart_btns_row1,
            text="💰 سعر",
            command=self.edit_price,
            fg_color=COLORS['secondary'],
            width=70
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            cart_btns_row1,
            text="🗑️ حذف",
            command=self.remove_from_cart,
            fg_color=COLORS['danger'],
            width=70
        ).pack(side="left", padx=2)
        
        # الصف الثاني من الأزرار
        cart_btns_row2 = ctk.CTkFrame(cart_btns, fg_color="transparent")
        cart_btns_row2.pack(fill="x")
        
        ctk.CTkButton(
            cart_btns_row2,
            text="� عملية بيع",
            command=self.quick_sale,
            fg_color="#8e44ad",
            width=110
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            cart_btns_row2,
            text="🗑️ مسح الكل",
            command=self.clear_cart,
            fg_color=COLORS['warning'],
            width=110
        ).pack(side="left", padx=2)
        
        # الإجمالي
        total_frame = ctk.CTkFrame(right_frame, fg_color=COLORS['primary'])
        total_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text="الإجمالي:",
            font=("Arial", 16, "bold")
        ).pack(side="right", padx=10, pady=15)
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="0.00 جنيه",
            font=("Arial", 20, "bold"),
            text_color="#ffffff"
        )
        self.total_label.pack(side="right", padx=10, pady=15)
        
        # زر الدفع
        pay_btn = ctk.CTkButton(
            right_frame,
            text="💳 دفع وإتمام البيع",
            command=self.process_sale,
            fg_color=COLORS['success'],
            hover_color="#1e8449",
            height=50,
            font=("Arial", 14, "bold")
        )
        pay_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        # تحميل البيانات
        self.load_categories()
        self.load_products()
    
    def load_customers(self):
        """تحميل العملاء"""
        self.customers = CustomerController.get_all_customers()
        customer_names = ["بدون عميل"] + [c['name'] for c in self.customers]
        self.customer_combo.configure(values=customer_names)
    
    def load_categories(self):
        """تحميل الأقسام"""
        self.categories = ProductController.get_all_categories()
        category_names = ["جميع الأقسام"] + [c['name'] for c in self.categories]
        self.category_combo.configure(values=category_names)
    
    def load_products(self):
        """تحميل المنتجات"""
        self.products_tree.delete(*self.products_tree.get_children())
        
        # تحديد القسم المختار
        category_id = self.get_selected_category_id()
        
        products = ProductController.get_all_products(category_id=category_id)
        for product in products:
            self.products_tree.insert(
                "",
                "end",
                values=(
                    product['name'],
                    f"{product['sell_price']:.2f}",
                    product['stock'],
                    product['barcode'] or ""
                ),
                tags=(product['id'],)
            )
    
    def search_products(self):
        """البحث عن المنتجات"""
        query = self.search_entry.get().strip()
        category_id = self.get_selected_category_id()
        
        self.products_tree.delete(*self.products_tree.get_children())
        
        products = ProductController.get_all_products(query, category_id)
        for product in products:
            self.products_tree.insert(
                "",
                "end",
                values=(
                    product['name'],
                    f"{product['sell_price']:.2f}",
                    product['stock'],
                    product['barcode'] or ""
                ),
                tags=(product['id'],)
            )
    
    def add_first_product(self):
        """إضافة أول منتج من نتائج البحث"""
        children = self.products_tree.get_children()
        if children:
            self.products_tree.selection_set(children[0])
            self.add_to_cart()
    
    def add_to_cart(self):
        """إضافة منتج للسلة"""
        selection = self.products_tree.selection()
        if not selection:
            return
        
        product_id = int(self.products_tree.item(selection[0])['tags'][0])
        product = ProductController.get_product_by_id(product_id)
        
        if not product:
            show_error("خطأ", "المنتج غير موجود")
            return
        
        if product['stock'] <= 0:
            show_error("خطأ", "المخزون غير كافي")
            return
        
        # التحقق إذا كان المنتج موجود في السلة
        for item in self.cart_items:
            if item['product_id'] == product_id:
                if item['quantity'] < product['stock']:
                    item['quantity'] += 1
                    self.update_cart_display()
                    return
                else:
                    show_error("خطأ", "المخزون غير كافي")
                    return
        
        # إضافة منتج جديد
        self.cart_items.append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['sell_price'],
            'quantity': 1
        })
        
        self.update_cart_display()
        self.search_entry.delete(0, 'end')
        self.search_entry.focus()
    
    def edit_quantity(self):
        """تعديل كمية المنتج في السلة"""
        selection = self.cart_tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار منتج من السلة")
            return
        
        index = self.cart_tree.index(selection[0])
        item = self.cart_items[index]
        
        # الحصول على المنتج للتحقق من المخزون
        product = ProductController.get_product_by_id(item['product_id'])
        if not product:
            show_error("خطأ", "المنتج غير موجود")
            return
        
        # نافذة تعديل الكمية
        dialog = SimpleInputDialog(
            self.winfo_toplevel(),
            title="تعديل الكمية",
            label=f"الكمية الجديدة للمنتج: {item['name']}",
            default_value=str(item['quantity']),
            validation_type="integer"
        )
        
        new_quantity = dialog.get_result()
        if new_quantity and new_quantity.strip():
            try:
                quantity = int(float(new_quantity))
                if quantity <= 0:
                    show_error("خطأ", "الكمية يجب أن تكون أكبر من صفر")
                    return
                
                # التحقق من المخزون المتاح (الحالي + الكمية في السلة)
                available_stock = product['stock'] + item['quantity']
                if quantity > available_stock:
                    show_error("خطأ", f"المخزون المتاح: {available_stock}")
                    return
                
                # تحديث الكمية
                self.cart_items[index]['quantity'] = quantity
                self.update_cart_display()
                
            except ValueError:
                show_error("خطأ", "يرجى إدخال رقم صحيح")
    
    def edit_price(self):
        """تعديل سعر المنتج في السلة"""
        selection = self.cart_tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار منتج من السلة")
            return
        
        index = self.cart_tree.index(selection[0])
        item = self.cart_items[index]
        
        # نافذة تعديل السعر
        dialog = SimpleInputDialog(
            self.winfo_toplevel(),
            title="تعديل السعر",
            label=f"السعر الجديد للمنتج: {item['name']}",
            default_value=str(item['price']),
            validation_type="number"
        )
        
        new_price = dialog.get_result()
        if new_price and new_price.strip():
            try:
                price = float(new_price)
                if price <= 0:
                    show_error("خطأ", "السعر يجب أن يكون أكبر من صفر")
                    return
                
                # تحديث السعر
                self.cart_items[index]['price'] = price
                self.update_cart_display()
                
            except ValueError:
                show_error("خطأ", "يرجى إدخال رقم صحيح")
    
    def remove_from_cart(self):
        """حذف من السلة"""
        selection = self.cart_tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار منتج من السلة")
            return
        
        index = self.cart_tree.index(selection[0])
        self.cart_items.pop(index)
        self.update_cart_display()
    
    def quick_sale(self):
        """بيع منفرد - إدخال عملية بيع بسيطة"""
        # نافذة البيع المنفرد
        dialog = ctk.CTkToplevel(self)
        dialog.title("عملية بيع منفردة")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # العنوان
        ctk.CTkLabel(
            dialog,
            text="� عملية بيع منفردة",
            font=("Arial", 18, "bold"),
            text_color=COLORS['primary']
        ).pack(pady=20)
        
        # إطار الحقول
        fields_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=10)
        
        # السبب/الوصف
        ctk.CTkLabel(
            fields_frame,
            text="السبب/الوصف:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", pady=(10, 5))
        
        reason_entry = ctk.CTkEntry(
            fields_frame,
            width=360,
            height=35,
            placeholder_text="مثال: خدمة، استشارة، منتج غير مسجل...",
            font=("Arial", 12)
        )
        reason_entry.pack(pady=5)
        reason_entry.focus()
        
        # المبلغ
        ctk.CTkLabel(
            fields_frame,
            text="المبلغ (جنيه):",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", pady=(15, 5))
        
        amount_entry = ctk.CTkEntry(
            fields_frame,
            width=360,
            height=35,
            placeholder_text="0.00",
            font=("Arial", 12)
        )
        amount_entry.pack(pady=5)
        
        def process_custom_sale():
            """معالجة البيع المنفرد"""
            reason = reason_entry.get().strip()
            if not reason:
                show_error("خطأ", "يرجى إدخال السبب/الوصف")
                return
            
            try:
                amount = float(amount_entry.get() or 0)
                if amount <= 0:
                    show_error("خطأ", "المبلغ يجب أن يكون أكبر من صفر")
                    return
            except ValueError:
                show_error("خطأ", "يرجى إدخال مبلغ صحيح")
                return
            
            # إنشاء عملية بيع خاصة (بدون منتج محدد)
            from database.connection import db
            
            try:
                # إنشاء رقم فاتورة
                invoice_number = f"CUSTOM-{db.fetch_one('SELECT COUNT(*) as count FROM sales')['count'] + 1:06d}"
                
                # إدخال البيع في قاعدة البيانات
                db.execute(
                    """INSERT INTO sales 
                       (invoice_number, user_id, total_amount, discount, payment_method, notes)
                       VALUES (?, ?, ?, 0, 'نقدي', ?)""",
                    (invoice_number, self.current_user['id'], amount, f"بيع منفرد: {reason}")
                )
                
                show_info(
                    "نجاح",
                    f"تم تسجيل العملية بنجاح!\n"
                    f"السبب: {reason}\n"
                    f"المبلغ: {amount:.2f} جنيه\n"
                    f"رقم الفاتورة: {invoice_number}"
                )
                
                dialog.destroy()
                self.update_daily_stats()  # تحديث الإحصائيات
                
            except Exception as e:
                show_error("خطأ", f"فشل في حفظ العملية: {str(e)}")
        
        # ربط Enter بالحقول
        reason_entry.bind('<Return>', lambda e: amount_entry.focus())
        amount_entry.bind('<Return>', lambda e: process_custom_sale())
        
        # الأزرار
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text="إلغاء",
            command=dialog.destroy,
            fg_color=COLORS['text_secondary'],
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="تسجيل العملية",
            command=process_custom_sale,
            fg_color=COLORS['success'],
            width=150
        ).pack(side="left", padx=5)
    
    def clear_cart(self):
        """مسح السلة"""
        if self.cart_items and ask_yes_no("تأكيد", "هل تريد مسح السلة؟"):
            self.cart_items = []
            self.update_cart_display()
    
    def update_cart_display(self):
        """تحديث عرض السلة"""
        self.cart_tree.delete(*self.cart_tree.get_children())
        
        total = 0
        for item in self.cart_items:
            item_total = item['price'] * item['quantity']
            total += item_total
            
            self.cart_tree.insert(
                "",
                "end",
                values=(
                    item['name'],
                    item['quantity'],
                    f"{item['price']:.2f}",
                    f"{item_total:.2f}"
                )
            )
        
        self.total_label.configure(text=f"{total:.2f} جنيه")
    
    def process_sale(self):
        """إتمام عملية البيع"""
        if not self.cart_items:
            show_error("خطأ", "السلة فارغة")
            return
        
        # الحصول على العميل
        customer_id = None
        customer_name = self.customer_var.get()
        if customer_name != "بدون عميل":
            for customer in self.customers:
                if customer['name'] == customer_name:
                    customer_id = customer['id']
                    break
        
        # إنشاء البيع
        result = SalesController.create_sale(
            user_id=self.current_user['id'],
            items=self.cart_items,
            customer_id=customer_id
        )
        
        if result['success']:
            show_info(
                "نجاح",
                f"تمت عملية البيع بنجاح!\n"
                f"رقم الفاتورة: {result['invoice_number']}\n"
                f"الإجمالي: {result['total']:.2f} جنيه"
            )
            
            # مسح السلة وتحديث المنتجات
            self.cart_items = []
            self.update_cart_display()
            self.load_products()
            # تحديث الإحصائيات بعد البيع
            self.update_daily_stats()
        else:
            show_error("خطأ", result['message'])
    
    def update_daily_stats(self):
        """تحديث إحصائيات اليوم"""
        # مبيعات اليوم
        sales_summary = SalesController.get_sales_summary()
        today_sales = sales_summary.get('total_revenue') or 0
        
        # مصاريف اليوم
        today_expenses = ExpenseController.get_today_total()
        
        # المبلغ في الدرج
        drawer_amount = today_sales - today_expenses
        
        # تحديث العرض
        self.sales_label.configure(
            text=f"مبيعات اليوم: {format_currency(today_sales)}"
        )
        self.expenses_label.configure(
            text=f"مصاريف اليوم: {format_currency(today_expenses)}"
        )
        
        drawer_color = COLORS['success'] if drawer_amount >= 0 else COLORS['danger']
        self.drawer_label.configure(
            text=f"في الدرج: {format_currency(drawer_amount)}",
            text_color=drawer_color
        )
    
    def add_quick_expense(self):
        """إضافة مصروف سريع"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("إضافة مصروف سريع")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # العنوان
        ctk.CTkLabel(
            dialog,
            text="💸 مصروف سريع",
            font=("Arial", 18, "bold"),
            text_color=COLORS['warning']
        ).pack(pady=20)
        
        # المبلغ
        ctk.CTkLabel(
            dialog,
            text="المبلغ:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        amount_entry = ctk.CTkEntry(
            dialog,
            width=320,
            height=35,
            placeholder_text="أدخل المبلغ",
            font=("Arial", 12)
        )
        amount_entry.pack(padx=40, pady=5)
        amount_entry.focus()
        
        # الوصف
        ctk.CTkLabel(
            dialog,
            text="الوصف:",
            font=("Arial", 12),
            text_color=COLORS['text']
        ).pack(anchor="e", padx=40, pady=(10, 5))
        
        description_entry = ctk.CTkEntry(
            dialog,
            width=320,
            height=35,
            placeholder_text="وصف المصروف",
            font=("Arial", 12)
        )
        description_entry.pack(padx=40, pady=5)
        
        def save_expense():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    show_error("خطأ", "المبلغ يجب أن يكون أكبر من صفر")
                    return
            except ValueError:
                show_error("خطأ", "المبلغ غير صحيح")
                return
            
            description = description_entry.get().strip()
            if not description:
                show_error("خطأ", "يجب إدخال وصف المصروف")
                return
            
            result = ExpenseController.add_expense(
                amount=amount,
                description=description,
                category="مصروف سريع",
                user_id=self.current_user['id']
            )
            
            if result['success']:
                show_info("نجاح", "تم إضافة المصروف بنجاح")
                dialog.destroy()
                self.update_daily_stats()
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
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="حفظ",
            command=save_expense,
            fg_color=COLORS['success'],
            width=150,
            height=35
        ).pack(side="left", padx=5)
        
        # ربط زر Enter بالحفظ
        dialog.bind('<Return>', lambda e: save_expense())
    
    def get_selected_category_id(self):
        """الحصول على معرف القسم المختار"""
        category_name = self.category_var.get()
        if category_name == "جميع الأقسام":
            return None
        
        for category in self.categories:
            if category['name'] == category_name:
                return category['id']
        return None
    
    def on_category_changed(self, value):
        """عند تغيير القسم المختار"""
        self.load_products()
    
    def open_returns_dialog(self):
        """فتح نافذة المرتجعات"""
        from ui.components.dialogs import ReturnsDialog
        from database.connection import db
        
        # الحصول على مبيعات آخر أسبوع (بما فيها اليوم)
        today_sales = db.fetch_all(
            """SELECT s.id, s.invoice_number, s.total_amount, s.created_at,
                      c.name as customer_name
               FROM sales s
               LEFT JOIN customers c ON s.customer_id = c.id
               WHERE DATE(s.created_at) >= DATE('now', '-7 days')
               ORDER BY s.created_at DESC"""
        )
        
        if not today_sales:
            show_info("معلومة", "لا توجد مبيعات في آخر أسبوع")
            return
        
        dialog = ReturnsDialog(self.winfo_toplevel(), today_sales)
        result = dialog.get_result()
        
        if result:
            # معالجة المرتجعات
            success_count = 0
            for item in result:
                response = SalesController.return_sale_item(
                    sale_id=item['sale_id'],
                    product_id=item['product_id'],
                    quantity=item['quantity']
                )
                if response['success']:
                    success_count += 1
            
            if success_count > 0:
                show_info("نجاح", f"تم استرجاع {success_count} منتج بنجاح")
                self.update_daily_stats()
            else:
                show_error("خطأ", "فشل استرجاع المنتجات")
