"""
شاشة إدارة المخزون
"""
import customtkinter as ctk
from tkinter import ttk
from config import COLORS
from controllers.product_controller import ProductController
from ui.components.dialogs import InputDialog, show_error, show_info, ask_yes_no
from ui.components.cards import StatCard


class InventoryView(ctk.CTkFrame):
    """شاشة المخزون"""
    
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color=COLORS['bg'])
        
        self.current_user = current_user
        self.categories = []
        self.create_widgets()
        self.load_categories()
        self.load_data()
    
    def create_widgets(self):
        """إنشاء العناصر"""
        # العنوان والإحصائيات
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="📦 إدارة المخزون",
            font=("Arial", 24, "bold")
        )
        title.pack(side="right")
        
        # الإحصائيات
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.total_products_card = StatCard(stats_frame, "إجمالي المنتجات", "0", "📦")
        self.total_products_card.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.total_value_card = StatCard(stats_frame, "قيمة المخزون", "0.00 جنيه", "💰", COLORS['success'])
        self.total_value_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.low_stock_card = StatCard(stats_frame, "منتجات منخفضة", "0", "⚠️", COLORS['warning'])
        self.low_stock_card.grid(row=0, column=2, padx=5, sticky="ew")
        self.low_stock_card.configure(cursor="hand2")
        self.low_stock_card.bind("<Button-1>", lambda e: self.show_low_stock_details())
        
        # البحث والتصفية
        search_filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_filter_frame.pack(fill="x", padx=20, pady=10)
        
        # الصف الأول: البحث النصي
        search_row = ctk.CTkFrame(search_filter_frame, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="البحث بالاسم أو الباركود...",
            width=300
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.load_data())
        
        # الصف الثاني: تصفية القسم
        filter_row = ctk.CTkFrame(search_filter_frame, fg_color="transparent")
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
        self.category_combo.pack(side="right", padx=5)
        
        # الأزرار
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            toolbar,
            text="📥 شراء متعدد",
            command=self.bulk_purchase,
            fg_color=COLORS['success'],
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="📦 منتجات متعددة",
            command=self.bulk_add_products,
            fg_color=COLORS['info'],
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="➕ منتج جديد",
            command=self.add_product,
            fg_color=COLORS['primary']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="✏️ تعديل",
            command=self.edit_product
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar,
            text="🗑️ حذف",
            command=self.delete_product,
            fg_color=COLORS['danger']
        ).pack(side="left", padx=5)
        
        # الجدول
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card_bg'])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("الاسم", "الفئة", "سعر البيع", "سعر الشراء", "المخزون", "التاجر", "الباركود")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="left", fill="y", pady=10)
    
    def load_categories(self):
        """تحميل الأقسام"""
        self.categories = ProductController.get_all_categories()
        category_names = ["جميع الأقسام"] + [c['name'] for c in self.categories]
        self.category_combo.configure(values=category_names)
    
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
        self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        query = self.search_entry.get().strip()
        category_id = self.get_selected_category_id()
        
        products = ProductController.get_all_products(query, category_id)
        
        self.tree.delete(*self.tree.get_children())
        
        for product in products:
            self.tree.insert(
                "",
                "end",
                values=(
                    product['name'],
                    product['category_name'] or "",
                    f"{product['sell_price']:.2f}",
                    f"{product['cost_price']:.2f}",
                    product['stock'],
                    product['trader_name'] or "",
                    product['barcode'] or ""
                ),
                tags=(product['id'],)
            )
        
        # تحديث الإحصائيات
        self.update_statistics()
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        products = ProductController.get_all_products()
        inventory_value = ProductController.get_total_inventory_value()
        low_stock = ProductController.get_low_stock_products()
        
        self.total_products_card.update_value(len(products))
        self.total_value_card.update_value(f"{inventory_value['total_sell']:.2f} جنيه")
        self.low_stock_card.update_value(len(low_stock))
    
    def add_product(self):
        """إضافة منتج"""
        from database.connection import db
        from ui.components.dialogs import ProductDialog
        
        # الحصول على البيانات المساعدة
        categories = db.fetch_all("SELECT * FROM categories ORDER BY name")
        suppliers = db.fetch_all("SELECT * FROM suppliers ORDER BY name")
        traders = db.fetch_all("SELECT * FROM external_traders ORDER BY name")
        
        # فتح نموذج الإضافة
        dialog = ProductDialog(
            self.winfo_toplevel(),
            title="إضافة منتج جديد",
            categories=categories,
            suppliers=suppliers,
            traders=traders
        )
        
        result = dialog.get_result()
        
        if result:
            # إضافة المنتج
            response = ProductController.add_product(result)
            
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def edit_product(self):
        """تعديل منتج"""
        from database.connection import db
        from ui.components.dialogs import ProductDialog
        
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار منتج")
            return
        
        product_id = int(self.tree.item(selection[0])['tags'][0])
        
        # الحصول على بيانات المنتج
        product = ProductController.get_product_by_id(product_id)
        
        if not product:
            show_error("خطأ", "المنتج غير موجود")
            return
        
        # الحصول على البيانات المساعدة
        categories = db.fetch_all("SELECT * FROM categories ORDER BY name")
        suppliers = db.fetch_all("SELECT * FROM suppliers ORDER BY name")
        traders = db.fetch_all("SELECT * FROM external_traders ORDER BY name")
        
        # فتح نموذج التعديل
        dialog = ProductDialog(
            self.winfo_toplevel(),
            title="تعديل منتج",
            product_data=product,
            categories=categories,
            suppliers=suppliers,
            traders=traders
        )
        
        result = dialog.get_result()
        
        if result:
            # تحديث المنتج
            response = ProductController.update_product(product_id, **result)
            
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def delete_product(self):
        """حذف منتج"""
        selection = self.tree.selection()
        if not selection:
            show_error("خطأ", "يرجى اختيار منتج")
            return
        
        if ask_yes_no("تأكيد", "هل تريد حذف هذا المنتج؟"):
            product_id = int(self.tree.item(selection[0])['tags'][0])
            result = ProductController.delete_product(product_id)
            
            if result['success']:
                show_info("نجاح", result['message'])
                self.load_data()
            else:
                show_error("خطأ", result['message'])
    
    def bulk_purchase(self):
        """إضافة عملية شراء متعددة المنتجات"""
        from ui.components.dialogs import BulkPurchaseDialog
        from database.connection import db
        
        # الحصول على قائمة المنتجات والموردين
        products = db.fetch_all("SELECT * FROM products ORDER BY name")
        suppliers = db.fetch_all("SELECT * FROM suppliers ORDER BY name")
        
        if not products:
            show_error("خطأ", "لا توجد منتجات في المخزون. يرجى إضافة منتجات أولاً.")
            return
        
        # فتح نموذج الشراء المتعدد
        dialog = BulkPurchaseDialog(
            self.winfo_toplevel(),
            products=products,
            suppliers=suppliers
        )
        
        result = dialog.get_result()
        
        if result:
            # معالجة عملية الشراء
            from controllers.purchase_controller import PurchaseController
            
            response = PurchaseController.process_bulk_purchase(
                supplier_id=result['supplier_id'],
                items=result['items'],
                user_id=self.current_user['id']
            )
            
            if response['success']:
                show_info("نجاح", response['message'])
                self.load_data()
            else:
                show_error("خطأ", response['message'])
    
    def bulk_add_products(self):
        """إضافة منتجات متعددة جديدة"""
        from ui.components.dialogs import BulkProductDialog
        from database.connection import db
        
        # الحصول على الفئات والموردين والتجار
        categories = db.fetch_all("SELECT * FROM categories ORDER BY name")
        suppliers = db.fetch_all("SELECT * FROM suppliers ORDER BY name")
        traders = db.fetch_all("SELECT * FROM external_traders ORDER BY name")
        
        if not categories:
            show_error("خطأ", "لا توجد فئات. يرجى إضافة فئة واحدة على الأقل أولاً.")
            return
        
        # فتح نموذج إضافة المنتجات المتعددة
        dialog = BulkProductDialog(
            self.winfo_toplevel(),
            categories=categories,
            suppliers=suppliers,
            traders=traders
        )
        
        result = dialog.get_result()
        
        if result:
            # حفظ جميع المنتجات
            success_count = 0
            error_count = 0
            
            for product_data in result:
                response = ProductController.add_product(product_data)
                if response['success']:
                    success_count += 1
                else:
                    error_count += 1
            
            if error_count == 0:
                show_info("نجاح", f"تم إضافة {success_count} منتج بنجاح!")
            else:
                show_info("تنبيه", f"تم إضافة {success_count} منتج بنجاح\nفشل {error_count} منتج")
            
            self.load_data()
    
    def show_low_stock_details(self):
        """عرض تفاصيل المنتجات المنخفضة"""
        low_stock_products = ProductController.get_low_stock_products()
        
        if not low_stock_products:
            show_info("معلومة", "لا توجد منتجات منخفضة في المخزون 👍")
            return
        
        # إنشاء نافذة التفاصيل
        from ui.components.dialogs import LowStockDialog
        dialog = LowStockDialog(self.winfo_toplevel(), low_stock_products)
        dialog.wait_window()
