import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import os

import config
from ui.base_window import BaseWindow
from models.product import ProductManager
from models.category import CategoryManager
from models.supplier import SupplierManager
from models.transaction import TransactionManager
from models.user import UserManager, RoleManager
from models.report import ReportManager
from utils.image_handler import get_image_handler
from utils.validators import create_validator, validate_price, validate_discount

class POSWindow(BaseWindow):
    """Main Point of Sale application window."""    
    def __init__(self, root, username):
        """Initialize the main POS window.
        
        Args:
            root: The root Tkinter window
            username: The logged-in username
        """
        super().__init__(root, "Point of Sale System", fullscreen=True)
        
        # Initialize models
        self.product_manager = ProductManager()
        self.category_manager = CategoryManager()
        self.supplier_manager = SupplierManager()
        self.transaction_manager = TransactionManager()
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        self.report_manager = ReportManager()
        self.image_handler = get_image_handler()
        
        # Initialize variables
        self.current_entry = None
        self.mode = "product_barcode"
        self.username = username
        self.new_image_path = None
        
        # Image storage to prevent garbage collection
        self.category_photos = {}
        self.product_photos = {}
        
        # Configure grid weights for the main layout
        self._configure_grid_weights()
        
        # Bind enter key
        self.root.bind('<Return>', lambda event: self.on_button_click("Enter"))
        
        # Setup the GUI components
        self.setup_gui()
    
    def _configure_grid_weights(self):
        """Configure the main grid weights."""
        for i in range(5):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
    
    def setup_gui(self):
        """Setup all GUI components."""
        self._setup_top_bar()
        self._setup_transaction_frame()
        self._setup_control_buttons()
        self._setup_product_selection_screen()
        self._create_keypad()
        self._setup_menu()
    
    def _setup_top_bar(self):
        """Setup the top bar with username, company name and time."""
        top_bar = tk.Frame(self.root, bg=config.COLORS["top_bar"])
        top_bar.grid(row=0, column=0, columnspan=100, sticky="NEW")
        
        self.root.grid_rowconfigure(0, weight=0)
        
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Username label
        username_label = tk.Label(
            top_bar, 
            text=self.username, 
            bg=config.COLORS["top_bar"], 
            fg="white"
        )
        username_label.grid(row=0, column=0, padx=10, sticky="NSW")
        
        # App name label
        company_label = tk.Label(
            top_bar, 
            text=config.APP_NAME, 
            bg=config.COLORS["top_bar"], 
            fg="white"
        )
        company_label.grid(row=0, column=1, padx=10, sticky="NSE")        
        
        # Time label
        self.time_label = tk.Label(
            top_bar, 
            text="", 
            bg=config.COLORS["top_bar"], 
            fg="white"
        )
        self.time_label.grid(row=0, column=2, padx=10, sticky="NSE")
        
        # Start time update
        self.update_time()
    
    def update_time(self):
        """Update the time display and schedule next update."""
        current_time = datetime.now().strftime("%A, %d %B %Y %H:%M")
        self.time_label.config(text=current_time)
        self.root.after(60000, self.update_time)  # Update every minute
    
    def _setup_transaction_frame(self):
        """Setup the transaction frame with treeview and controls."""
        # Configure treeview style
        self._configure_treeview_style()
        
        # Create transaction frame
        self.transaction_frame = tk.Frame(
            self.root, 
            bg=config.COLORS["transaction_frame"], 
            bd=2, 
            relief="raised", 
            highlightthickness=1
        )
        self.transaction_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="NSEW")
        
        # Create transaction treeview
        self.transaction_tree = ttk.Treeview(
            self.transaction_frame, 
            columns=("Barcode", "Name", "Quantity", "Total", "Discount"), 
            height=12, 
            show="headings", 
            selectmode="browse"
        )
        
        # Configure treeview columns
        self._configure_transaction_tree_columns()
        
        # Configure treeview tags
        self.transaction_tree.tag_configure("evenrow", background="#f5f5f5")
        self.transaction_tree.tag_configure("oddrow", background="#ffffff")
        
        # Place treeview in grid
        self.transaction_tree.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="NSEW")
        
        # Setup navigation buttons
        self._setup_transaction_navigation()
        
        # Setup total label, entry label and entry
        self.total_label = tk.Label(
            self.transaction_frame, 
            text="Total: $0.00", 
            font=config.FONTS["header"]
        )
        self.total_label.grid(row=1, column=0, padx=10, pady=10, sticky="NSW")
        
        self.entry_label = tk.Label(
            self.transaction_frame, 
            text="Product Barcode:", 
            font=config.FONTS["entry"]
        )
        self.entry_label.grid(row=2, column=0, padx=10, pady=10, sticky="NSW")
        
        # Create validation command for price input
        self.vcmd = create_validator(self.transaction_frame, validate_price)
        
        self.entry = tk.Entry(self.transaction_frame, font=config.FONTS["entry"])
        self.entry.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky="EW")
        self.entry.focus()
        
        # Set the current entry widget
        self.current_entry = self.entry
        
        # Configure transaction frame grid
        self.transaction_frame.grid_columnconfigure(0, weight=0)
        self.transaction_frame.grid_columnconfigure(1, weight=1)
        self.transaction_frame.grid_rowconfigure(0, weight=1)
        self.transaction_frame.grid_rowconfigure(1, weight=1)
        self.transaction_frame.grid_rowconfigure(2, weight=1)
    
    def _configure_treeview_style(self):
        """Configure the treeview style"""
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#f0f0f0",
            foreground="#000000",
            rowheight=35,
            fieldbackground="#ffffff",
            font=("Segoe UI", 16)
        )
        
        style.configure(
            "Treeview.Heading", 
            font=("Segoe UI", 12, "bold"),
            padding=[10, 5, 10, 5]
        )
                
        style.map(
            "Treeview", 
            background=[("selected", "#4CAF50")],
            foreground=[("selected", "#FFFFFF")]
        )
    
    def _configure_transaction_tree_columns(self):
        """Configure the transaction treeview columns"""
        # Configure column headings
        self.transaction_tree.heading("Barcode", text="Barcode", anchor="w")
        self.transaction_tree.heading("Name", text="Name", anchor="w")
        self.transaction_tree.heading("Quantity", text="Quantity", anchor="e")
        self.transaction_tree.heading("Total", text="Total", anchor="e")
        self.transaction_tree.heading("Discount", text="Discount", anchor="e")

        # Configure column widths and anchors
        self.transaction_tree.column("Barcode", width=100, anchor="w")
        self.transaction_tree.column("Name", width=270, anchor="w")
        self.transaction_tree.column("Quantity", width=75, anchor="e")
        self.transaction_tree.column("Total", width=100, anchor="e")
        self.transaction_tree.column("Discount", width=55, anchor="e")
    
    def _setup_transaction_navigation(self):
        """Setup transaction navigation buttons"""
        self.transaction_frame_nav = tk.Frame(
            self.transaction_frame, 
            background=self.transaction_frame.cget("bg")
        )
        self.transaction_frame_nav.grid(row=0, column=2, sticky="NSEW")
        
        # Create navigation buttons
        nav_buttons = [
            ("↑↑", self.go_top, 0),
            ("↑", self.go_up, 1),
            ("↓", self.go_down, 2),
            ("↓↓", self.go_bottom, 3)
        ]
        
        for text, command, row in nav_buttons:
            button = tk.Button(
                self.transaction_frame_nav, 
                text=text, 
                command=command, 
                font=config.FONTS["entry"]
            )
            button.grid(row=row, column=0, padx=5, pady=5, sticky="NSEW")

        # Configure navigation grid
        for i in range(4):
            self.transaction_frame_nav.grid_rowconfigure(i, weight=1, uniform="equal")
        self.transaction_frame_nav.grid_columnconfigure(0, weight=1, uniform="equal")
    
    def _setup_control_buttons(self):
        """Setup control buttons frame"""
        self.control_buttons = tk.Frame(
            self.root, 
            background=config.COLORS["control_buttons"], 
            bd=2, 
            relief="raised", 
            highlightthickness=1
        )
        self.control_buttons.grid(row=2, column=0, padx=20, pady=20, rowspan=5, sticky="NSW")
        
        size = 16  # Button font size
        
        # Define button configurations (text, command, row, column)
        button_configs = [
            ("Product Barcode", self.set_product_barcode_mode, 0, 0),
            ("Product Enquiry", self.set_product_enquiry_mode, 1, 0),
            ("Quantity", self.set_quantity_mode, 2, 0),
            ("Discount", self.set_discount_item_mode, 3, 0),
            ("Clear", lambda: self.on_button_click("Clear"), 0, 1),
            ("Void Line", self.remove_product_from_selected, 1, 1),
            ("Void Transaction", self.void_transaction, 2, 1),
            ("Log Out", self.logout, 3, 1)
        ]
        
        # Create buttons from configuration
        for text, command, row, col in button_configs:
            button = tk.Button(
                self.control_buttons, 
                text=text, 
                command=command, 
                font=("Segoe UI Semibold", size)
            )
            button.grid(row=row, column=col, padx=5, pady=5, sticky="NSEW")

        # Configure control grid for equal button sizes
        for i in range(2):
            self.control_buttons.grid_columnconfigure(i, weight=1, uniform="equal")
        for i in range(4):
            self.control_buttons.grid_rowconfigure(i, weight=1, uniform="equal")
    
    def _setup_menu(self):
        """Setup the application menu"""
        menubar = tk.Menu(self.root)

        # Create sub-menus
        file_menu = tk.Menu(menubar, tearoff=False)
        product_menu = tk.Menu(menubar, tearoff=False)
        cat_menu = tk.Menu(menubar, tearoff=False)
        user_menu = tk.Menu(menubar, tearoff=False)
        sup_menu = tk.Menu(menubar, tearoff=False)

        # Add menus to menubar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Products", menu=product_menu)
        menubar.add_cascade(label="Categories", menu=cat_menu)
        menubar.add_cascade(label="Users", menu=user_menu)
        menubar.add_cascade(label="Suppliers", menu=sup_menu)

        # File menu items
        file_menu.add_command(label="Monthly Report", command=self.monthly_profit_window)
        file_menu.add_command(label="Sales History", command=self.sales_history_window)

        # Product menu items
        product_menu.add_command(label="View All Products", command=self.view_products_window)
        product_menu.add_command(label="Add New Product", command=self.add_product_window)
        product_menu.add_command(label="Edit a Product", command=self.edit_product_window)
        product_menu.add_command(label="Remove a Product", command=self.remove_product_window)
        product_menu.add_command(label="Set Stock", command=self.update_stock_window)

        # Category menu items
        cat_menu.add_command(label="Manage Categories", command=self.manage_categories_window)
        
        # User menu items
        user_menu.add_command(label="Manage Users", command=self.manage_users_window)
        user_menu.add_command(label="Manage Roles", command=self.manage_roles_window)
        
        # Supplier menu items
        sup_menu.add_command(label="Manage Suppliers", command=self.manage_suppliers_window)

        # Exit menu item
        menubar.add_command(label="Exit", command=self.close_app)

        # Set the menubar
        self.root.config(menu=menubar)
    
    # Navigation methods
    def go_up(self):
        """Scroll transaction tree up one unit"""
        self.transaction_tree.yview_scroll(1, "units")

    def go_down(self):
        """Scroll transaction tree down one unit"""
        self.transaction_tree.yview_scroll(-1, "units")

    def go_top(self):
        """Scroll transaction tree to the top"""
        self.transaction_tree.yview_moveto(1)

    def go_bottom(self):
        """Scroll transaction tree to the bottom"""
        self.transaction_tree.yview_moveto(0)
    
    def logout(self):
        """Handle user logout"""
        result = self.confirm("Are you sure you want to log out?", "Log Out")
        if result:
            # Reset the alert manager singleton so it gets recreated with the new root
            import utils.alerts
            utils.alerts._alert_manager = None
            
            # Destroy the current window completely
            self.root.destroy()
            
            # Restart the application with login window
            import tkinter as tk
            from ui.login_window import LoginWindow
            new_root = tk.Tk()
            login_window = LoginWindow(new_root)
            login_window.run()
    
    def close_app(self):
        """Close the application after confirmation"""
        result = self.confirm("Are you sure you want to exit?", "Close Application")
        if result:
            self.root.quit()
    
    # Mode setting methods
    def set_quantity_mode(self):
        """Switch to quantity entry mode"""
        self.mode = "quantity"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
        self.entry_label.config(text="Quantity:")

    def set_product_barcode_mode(self):
        """Switch to product barcode entry mode"""
        self.mode = "product_barcode"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
        self.entry_label.config(text="Product Barcode:")

    def set_discount_item_mode(self):
        """Switch to discount entry mode"""
        self.mode = "discount"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
        self.entry_label.config(text="Discount Item (%):")

    def set_product_enquiry_mode(self):
        """Switch to product enquiry mode"""
        self.mode = "product enquiry"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
        self.entry_label.config(text="Product Enquiry:")

    def set_pay_mode(self):
        """Switch to payment mode"""
        self.mode = "pay"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
        self.entry_label.config(text="Cash Received: ")
    
    # Keypad and entry handling
    def _create_keypad(self):
        """Create the numeric keypad for input."""
        self.keypad_frame = tk.Frame(self.root, background=config.COLORS["keypad"])
        self.keypad_frame.grid(row=2, column=1, rowspan=5, columnspan=1, padx=20, pady=20, sticky="NSEW")

        # Button layout and spans
        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2), ("Pay", 0, 3, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("Enter", 2, 3, 2),
            ("⌫", 3, 0), ("0", 3, 1), (".", 3, 2)
        ]

        for button in buttons:
            text = button[0]
            row = button[1]
            col = button[2]
            rowspan = button[3] if len(button) > 3 else 1
            button_widget = tk.Button(
                self.keypad_frame, 
                text=text, 
                command=lambda t=text: self.on_button_click(t), 
                font=config.FONTS["keypad_button"], 
                relief=tk.RAISED
            )
            button_widget.grid(row=row, column=col, rowspan=rowspan, sticky="NSEW", padx=5, pady=5)

        # Configure grid for equal button sizes
        for i in range(4):
            self.keypad_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        for i in range(4):
            self.keypad_frame.grid_rowconfigure(i, weight=1, uniform="equal")

        # Bind all entry widgets
        self.bind_all_entries()
    
    def on_button_click(self, char):
        """Handle keypad button clicks"""
        if not self.current_entry:
            return
            
        current_text = self.current_entry.get()
        
        if char == "⌫":
            # Backspace - delete last character
            self.current_entry.delete(len(current_text) - 1, tk.END)
        elif char == "Clear":
            # Clear - delete all text
            self.current_entry.delete(0, tk.END)
        elif char in ("Pay", "Enter"): 
            if char == "Enter":
                self.process_entry()
            elif char == "Pay":
                self.pay_mode()
        else:
            # Add the character to the entry
            self.current_entry.insert(tk.END, char)
    
    def process_entry(self):
        """Process the current entry based on the active mode"""
        if not self.current_entry:
            return
            
        input_value = self.current_entry.get()
        
        if not input_value:
            self.show_error("Please enter a value.")
            return
            
        if self.mode == "quantity":
            self.alter_quantity(input_value)
        elif self.mode == "product_barcode":
            self.add_to_transaction(product_barcode=input_value)
        elif self.mode == "discount":
            self.discount_item_from_selected(input_value)
        elif self.mode == "product enquiry":
            self.display_product_enquiry(input_value)
            self.set_product_barcode_mode()
        elif self.mode == "pay":
            self.calculate_change(input_value)

        self.current_entry.delete(0, tk.END)
    
    def set_current_entry(self, event):
        """Set the current entry widget when focus changes"""
        self.current_entry = event.widget
    
    def bind_all_entries(self):
        """Bind all entry widgets to focus event"""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.bind("<FocusIn>", self.set_current_entry)
            elif isinstance(widget, tk.Frame):
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, tk.Entry):
                        sub_widget.bind("<FocusIn>", self.set_current_entry)
    
    # Transaction management methods
    def add_to_transaction(self, product_id=None, product_barcode=None):
        """Add a product to the current transaction"""
        success = False
        message = ""
        
        # Add product via product_id or product_barcode
        if product_id:
            success, message, _ = self.transaction_manager.add_product_to_transaction(product_id=product_id)
        elif product_barcode:
            success, message, _ = self.transaction_manager.add_product_to_transaction(product_barcode=product_barcode)
        else:
            self.show_error("No product ID or barcode provided")
            return
        
        if success:
            # Update the transaction display
            self.update_transaction()
            
            # Show any notifications
            if message:
                product = self.product_manager.fetch_product_by_barcode(product_barcode) or self.product_manager.fetch_product_by_id(product_id)
                if product:
                    self.show_info(product[1], message)  # Use product name
        else:
            self.show_error(message)
    
    def update_transaction(self):
        """Update the transaction display with current items"""
        # Clear current display
        self.transaction_tree.delete(*self.transaction_tree.get_children())
        
        # Get all products in the transaction
        selected_products = self.transaction_manager.get_transaction_products()
        
        # Calculate total
        total = self.transaction_manager.calculate_total()
        
        # Add each product to the display
        last_iid = None
        for index, product in enumerate(selected_products):
            discount = ""
            if product[5] and product[5] != 0:
                discount = f"{product[5]}%"

            color_tag = "evenrow" if index % 2 == 0 else "oddrow"

            # Insert item with its UUID as the iid
            iid = product[0]
            self.transaction_tree.insert(
                parent="",
                index=tk.END,
                iid=iid,
                values=(product[1], product[2], product[3], f"{product[4]:.2f}", discount),
                tags=(color_tag,)
            )
            last_iid = iid
        
        # Update total
        self.total_label.config(text=f"Total: ${total:.2f}")
        
        # Scroll to bottom
        self.transaction_tree.yview_moveto(1)

        # Select the last item if exists
        if last_iid is not None:
            self.transaction_tree.focus(last_iid)
            self.transaction_tree.selection_set(last_iid)
    
    def alter_quantity(self, new_quantity):
        """Change the quantity of a selected product in the transaction"""
        # Get selected item
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            self.show_error("Please select a product.")
            return
        
        # Validate quantity
        try:
            qty = int(new_quantity)
            if qty <= 0:
                self.show_error("Invalid quantity provided.")
                return
        except ValueError:
            self.show_error("Invalid quantity provided.")
            return
        
        # Get selected item ID
        selected_iid = selected_item[0]
        
        # Update the quantity
        success, message = self.transaction_manager.alter_quantity(selected_iid, qty)
        
        if success:
            # Update the transaction display
            self.update_transaction()
            self.set_product_barcode_mode()
        else:
            self.show_error(message)
    
    def remove_product_from_selected(self):
        """Remove a selected product from the transaction"""
        # Get selected item
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            self.show_error("Please select a product.")
            return

        # Get selected item ID
        selected_iid = selected_item[0]

        # Remove the product
        success, message = self.transaction_manager.remove_product(selected_iid)
        
        if success:
            # Update the transaction display
            self.update_transaction()
        else:
            self.show_error(message)
    
    def void_transaction(self):
        """Clear the entire current transaction"""
        result = self.confirm("Clear the entire current transaction? This cannot be undone.", "Void Transaction")
        if result:
            # Clear the transaction
            self.transaction_manager.clear_transaction()
            if self.current_entry:
                self.current_entry.delete(0, tk.END)
            
            # Update the transaction display
            self.update_transaction()
    
    def discount_item_from_selected(self, discount_amount):
        """Apply a discount to a selected item in the transaction"""
        # Get selected item
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            self.show_error("Please select a product.")
            return
        
        # Validate discount
        try:
            discount = float(discount_amount)
            if discount < 0 or discount > 100:
                self.show_error("Invalid discount provided. Must be between 0 and 100.")
                return
        except ValueError:
            self.show_error("Invalid discount provided.")
            return
        
        # Get selected item ID
        selected_iid = selected_item[0]
        
        # Apply the discount
        success, message = self.transaction_manager.apply_discount(selected_iid, discount)
        
        if success:
            # Update the transaction display
            self.update_transaction()
            if self.current_entry:
                self.current_entry.delete(0, tk.END)
            self.set_product_barcode_mode()
        else:
            self.show_error(message)
    
    def pay_mode(self):
        """Enter payment mode for completing a transaction"""
        # Check if transaction is empty
        if not self.transaction_manager.get_transaction_products():
            self.show_error("No items in transaction.")
            return
            
        # Create payment window frame
        self.pay_window = tk.Frame(
            self.transaction_frame, 
            bg=config.COLORS["pay_frame"], 
            bd=1, 
            relief="solid"
        )
        self.pay_window.grid(row=0, column=0, rowspan=2, columnspan=5, sticky="NSEW")

        # Configure grid
        for i in range(2):
            self.pay_window.grid_columnconfigure(i, weight=1)
        for i in range(3):
            self.pay_window.grid_rowconfigure(i, weight=1)

        # Total amount display
        tk.Label(
            self.pay_window, 
            text="Total Amount:", 
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="NW")
        
        tk.Label(
            self.pay_window, 
            text=self.total_label.cget("text"), 
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        ).grid(row=0, column=1, padx=10, pady=5, sticky="NEW")

        # Cash received display
        tk.Label(
            self.pay_window, 
            text="Cash Received:", 
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        ).grid(row=1, column=0, padx=10, pady=5, sticky="NW")
        
        self.cash_received = tk.Label(
            self.pay_window, 
            text="", 
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        )
        self.cash_received.grid(row=1, column=1, padx=10, pady=5, sticky="NEW")
        
        # Change display
        tk.Label(
            self.pay_window, 
            text="Change:",
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        ).grid(row=2, column=0, padx=10, pady=5, sticky="NW")
        
        self.change_label = tk.Label(
            self.pay_window, 
            text="$0.00", 
            font=config.FONTS["pay_label"],
            bg=config.COLORS["pay_frame"],
            fg="white"
        )
        self.change_label.grid(row=2, column=1, padx=10, pady=5, sticky="NEW")

        def exit_pay_mode():
            """Exit payment mode"""
            self.pay_window.destroy()
            self.set_product_barcode_mode()
            self.enable_widgets(self.category_inner_frame, self.control_buttons)

        # Exit and Calculate buttons
        tk.Button(
            self.pay_window, 
            text="Exit Pay Mode", 
            command=exit_pay_mode, 
            font=config.FONTS["button"]
        ).grid(row=3, column=0, padx=10, pady=5, sticky="NSEW")
        
        # Calculate button - this will trigger the calculate_change method
        tk.Button(
            self.pay_window, 
            text="Calculate Change", 
            command=lambda: self.calculate_change(self.current_entry.get()), 
            font=config.FONTS["button"]
        ).grid(row=3, column=1, padx=10, pady=5, sticky="NSEW")

        # Switch to pay mode
        self.set_pay_mode()
        # Disable other UI elements during payment
        self.disable_widgets(self.category_inner_frame, self.control_buttons)
    
    def calculate_change(self, cash_received_str):
        """Calculate change for a transaction payment"""
        try:
            # Calculate total from transaction items
            total_amount = self.transaction_manager.calculate_total()
            
            cash_received = float(cash_received_str) 
            
            # Validate cash amount
            if cash_received < total_amount:
                self.show_error("Cash received is less than the total amount.")
                return
                
            # Calculate and display change
            change = cash_received - total_amount
            self.change_label.config(text=f"${change:.2f}")
            self.cash_received.config(text=f"${cash_received:.2f}")
            
            # Confirm and complete sale
            if self.confirm(f"Change: ${change:.2f}\nComplete the Sale?", "Confirm Payment"):
                success, message, change_amount, transaction_id = self.transaction_manager.complete_sale(cash_received, self.username)
                
                if success:
                    self.pay_window.destroy()
                    self.set_product_barcode_mode()
                    self.enable_widgets(self.category_inner_frame, self.control_buttons)
                    # Update the display
                    self.update_transaction()
                else:
                    self.show_error(message)
                
        except ValueError:
            self.show_error("Invalid cash received. e")
        except Exception as e:
            self.show_error(str(e))
    
    def display_product_enquiry(self, barcode):
        """Display details for a product based on its barcode"""
        # Use the ProductManager to fetch the product
        product_data = self.product_manager.fetch_product_by_barcode(barcode)

        if not product_data:
            self.show_error("Product not found.")
            return

        # Create product details dictionary
        category = self.category_manager.fetch_category_by_id(product_data[2])
        supplier = self.supplier_manager.fetch_supplier_by_id(product_data[7])
        
        product_details = {
            "name": product_data[1],
            "category": category[1] if category else "Unknown",
            "price": product_data[3],
            "stock": product_data[4],
            "barcode": product_data[5],
            "description": product_data[6],
            "supplier": supplier if supplier else "Unknown",
            "discount": product_data[8],
            "unit": product_data[9],
            "date_added": product_data[10],
            "is_alcoholic": product_data[11] == 1,
            "is_active": product_data[12] == 1,
        }

        # Create modal frame
        product_enquiry_frame = tk.Frame(self.root, bg="white", bd=2, relief="ridge")
        product_enquiry_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Add title
        title_label = tk.Label(
            product_enquiry_frame, 
            text="Product Enquiry", 
            bg="white", 
            fg="black", 
            font=config.FONTS["header"]
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

        # Create details frame
        details_frame = tk.Frame(product_enquiry_frame, bg="white")
        details_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=2)

        # Format details
        details = [
            ("Product Name", product_details["name"]),
            ("Category", product_details["category"]),
            ("Price", f"${product_details['price']:.2f}"),
            ("Stock", product_details["stock"]),
            ("Barcode", product_details["barcode"]),
            ("Description", product_details["description"]),
            ("Supplier", product_details["supplier"]),
            ("Discount", f"{product_details['discount']}%"),
            ("Unit", product_details["unit"]),
            ("Date Added", product_details["date_added"]),
            ("Alcoholic", "Yes" if product_details["is_alcoholic"] else "No"),
            ("Active", "Yes" if product_details["is_active"] else "No"),
        ]

        # Display details
        row_count = 0
        for i, (key, value) in enumerate(details):
            key_label = tk.Label(details_frame, text=f"{key}:", bg="white", anchor="e", font=config.FONTS["default"])
            key_label.grid(row=i, column=0, sticky="e", padx=10, pady=5)

            value_label = tk.Label(details_frame, text=value, bg="white", fg="black", anchor="w", font=config.FONTS["default"] )
            value_label.grid(row=i, column=1, sticky="w", padx=10, pady=5)
            
            row_count = i

        # Add close button
        close_button = tk.Button(
            product_enquiry_frame, 
            text="Close", 
            bg="#73bf65", 
            command=product_enquiry_frame.destroy,
            font=config.FONTS["button"]
        )
        close_button.grid(row=row_count+1, column=0, columnspan=2, pady=10, padx=10, sticky="NSEW")

    # Product selection screen
    def _setup_product_selection_screen(self):
        """Setup the product category selection screen"""
        self.category_frame = tk.Frame(self.root, bg=config.COLORS["category_frame"])
        self.category_frame.grid(row=1, column=2, rowspan=4, columnspan=3, padx=20, pady=20, sticky="NSEW")

        self.category_frame.grid_rowconfigure(0, weight=1)
        self.category_frame.grid_columnconfigure(0, weight=1)

        self.category_canvas = tk.Canvas(self.category_frame, bg=config.COLORS["category_frame"])
        self.category_canvas.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="NSEW")

        self.category_scrollbar = ttk.Scrollbar(self.category_frame, orient="vertical", command=self.category_canvas.yview)
        self.category_scrollbar.grid(row=0, column=1, sticky="NS")

        self.category_canvas.configure(yscrollcommand=self.category_scrollbar.set)

        self.category_canvas.update_idletasks()
        self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all"))

        self.category_inner_frame = tk.Frame(self.category_canvas, bg=config.COLORS["category_frame"])

        self.category_inner_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        self.category_inner_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        self.category_inner_frame.grid_columnconfigure(2, weight=1, uniform="equal")

        self.category_canvas_window = self.category_canvas.create_window(
            (0, 0), 
            window=self.category_inner_frame, 
            anchor="nw"
        )

        self.category_canvas.bind("<Configure>", 
            lambda e: self.category_canvas.itemconfig(self.category_canvas_window, width=e.width)
        )

        def _on_mousewheel(event):
            self.category_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.category_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.category_inner_frame.bind("<Configure>", 
            lambda e: self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all"))
        )
        
        # Display all categories
        self.display_categories()
    
    def display_categories(self):
        """Display all categories in the category frame"""
        # Clear existing widgets
        for widget in self.category_inner_frame.winfo_children():
            widget.destroy()

        # Configure grid
        self.category_inner_frame.grid_rowconfigure(0, weight=1)
        self.category_inner_frame.grid_columnconfigure(0, weight=1)

        # Get all categories
        categories = self.category_manager.fetch_all_categories()
        
        # Create a dictionary to store photo references so they don't get garbage collected
        self.category_photos = {}

        # Display each category as a button with image
        for idx, category in enumerate(categories):
            row = idx // 3
            col = idx % 3

            # Create frame for this category
            category_item_frame = tk.Frame(self.category_inner_frame, bg=self.category_inner_frame.cget("bg"))
            category_item_frame.grid(row=row, column=col, padx=10, pady=10, sticky="NSEW")

            # Configure grid
            category_item_frame.grid_rowconfigure(0, weight=1)
            category_item_frame.grid_rowconfigure(1, weight=1)
            category_item_frame.grid_columnconfigure(0, weight=1)

            # Load category image if available
            image_path = None
            if hasattr(category, '__getitem__') and len(category) > 3:
                image_path = category[3] if category[3] else None
            
            # Load the image (will use default if path is invalid)
            photo = self.image_handler.load_product_image(image_path, size=(200, 200), master=self.category_inner_frame)
            print(f"DEBUG: Photo object created: {photo}, type: {type(photo)}")

            # Store reference to prevent garbage collection
            self.category_photos[f"cat_{category[0]}"] = photo
            print(f"DEBUG: Photo stored in self.category_photos with key 'cat_{category[0]}'")
            
            # Add image
            if photo:
                image_label = tk.Label(category_item_frame, image=photo, bg=self.category_inner_frame.cget("bg"))
                image_label.image = photo
                image_label.grid(row=0, column=0, sticky="NSEW")
                image_label.bind("<Button-1>", lambda event, c=category[0]: self.display_products(c))

            # Add category button
            category_button = tk.Button(
                category_item_frame, 
                text=category[1], 
                command=lambda c=category[0]: self.display_products(c),
                font=("Segoe UI Semibold", 15)
            )
            category_button.grid(row=1, column=0, sticky="NSEW")
    
    def display_products(self, category_id):
        """Display products for a selected category"""
        # Clear existing widgets
        for widget in self.category_inner_frame.winfo_children():
            widget.destroy()

        # Get products for this category
        products = self.product_manager.fetch_products_by_category(category_id)

        # Add back button
        back_button = tk.Button(
            self.category_inner_frame, 
            text="<< Back to Categories <<", 
            command=self.display_categories,
            font=("Segoe UI Semibold", 15)
        )
        back_button.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="NSEW")

        # Create a dictionary to store photo references so they don't get garbage collected
        self.product_photos = {}

        # Display each product
        for idx, product in enumerate(products):
            row = idx // 3 + 1  # +1 to account for back button
            col = idx % 3

            # Create frame for this product
            product_frame = tk.Frame(self.category_inner_frame, bg=self.category_inner_frame.cget("bg"))
            product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="NSEW")

            # Configure grid
            product_frame.grid_rowconfigure(0, weight=1)
            product_frame.grid_rowconfigure(1, weight=1)
            product_frame.grid_columnconfigure(0, weight=1)

            # Get image path if available
            image_path = None
            if hasattr(product, '__getitem__') and len(product) > 13:
                image_path = product[13]
            
            # Load the image (will use default if path is invalid)
            # Pass the proper master widget (product_frame) to ensure the PhotoImage is associated with the right context
            photo = self.image_handler.load_product_image(image_path, size=(200, 200), master=product_frame)
            
            # Store reference to prevent garbage collection with a unique key
            photo_key = f"prod_{product[0]}_{idx}"
            self.product_photos[photo_key] = photo
            print(f"DEBUG: Product photo stored with key '{photo_key}'")
            
            # Add image
            image_label = tk.Label(product_frame, image=photo, bg=self.category_inner_frame.cget("bg"))
            image_label.grid(row=0, column=0, sticky="NSEW")
            image_label.bind("<Button-1>", lambda event, p=product: self.add_to_transaction(product_id=p[0]))
            
            # Store a reference to the photo in the label to prevent garbage collection
            image_label.image = photo

            # Add product button
            product_button = tk.Button(
                product_frame, 
                text=product[1],
                command=lambda p=product: self.add_to_transaction(product_id=p[0]),
                font=("Segoe UI Semibold", 15)
            )
            product_button.grid(row=1, column=0, sticky="NSEW")
    
    # Category management window
    def manage_categories_window(self):
        """Open window to manage product categories with image support"""
        category_window = tk.Toplevel(self.root)
        category_window.title("Manage Categories")
        category_window.resizable(True, True)
        category_window.attributes("-topmost", True)

        # Split layout
        list_frame = tk.Frame(category_window)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_frame = tk.Frame(category_window)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create category tree
        tk.Label(list_frame, text="Categories", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        category_tree = ttk.Treeview(
            list_frame, 
            columns=("ID", "Name", "Discount", "Has Image"), 
            show="headings",
            height=15
        )
        category_tree.heading("ID", text="ID")
        category_tree.heading("Name", text="Name")
        category_tree.heading("Discount", text="Discount %")
        category_tree.heading("Has Image", text="Has Image")
        
        category_tree.column("ID", width=50, anchor="w")
        category_tree.column("Name", width=150, anchor="w")
        category_tree.column("Discount", width=100, anchor="e")
        category_tree.column("Has Image", width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=category_tree.yview)
        category_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Category details form
        tk.Label(details_frame, text="Category Details", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        
        # Category ID (hidden)
        category_id_var = tk.StringVar()
        
        # Category name
        tk.Label(details_frame, text="Category Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        category_name_entry = tk.Entry(details_frame, width=30)
        category_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Discount
        tk.Label(details_frame, text="Discount (%):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        category_discount_entry = tk.Entry(details_frame, width=10)
        category_discount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Image section
        image_frame = tk.Frame(details_frame)
        image_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Image display
        image_label = tk.Label(image_frame, text="No image selected", width=20, height=10, relief="solid")
        image_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Current image path (hidden)
        current_image_path = None
        
        def load_category_images():
            """Load and display the category image"""
            if hasattr(self, 'category_image_photo'):
                delattr(self, 'category_image_photo')
                
            if current_image_path:
                try:
                    photo = self.image_handler.load_product_image(current_image_path, size=(150, 150), master=image_label)
                    image_label.config(image=photo, text="")
                    # Keep a reference to prevent garbage collection
                    self.category_image_photo = photo
                except Exception as e:
                    image_label.config(image="", text="Image not found")
                    print(f"Error loading image: {e}")
            else:
                image_label.config(image="", text="No image selected")
        
        def select_image():
            """Select an image file for the category"""
            nonlocal current_image_path
            image_path = filedialog.askopenfilename(
                title="Select Category Image", 
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if image_path:
                current_image_path = image_path
                load_category_images()
        
        # Image selection button
        image_button = tk.Button(image_frame, text="Select Image", command=select_image)
        image_button.grid(row=0, column=1, padx=10, pady=5, sticky="n")
        
        # Status indicator
        status_label = tk.Label(details_frame, text="", font=("Segoe UI", 10))
        status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")
        
        def load_categories():
            """Load all categories into the treeview"""
            category_tree.delete(*category_tree.get_children())
            categories = self.category_manager.fetch_all_categories()
            for category in categories:
                # Check if the category has an image
                has_image = "Yes" if category[3] else "No"
                category_tree.insert("", tk.END, values=(category[0], category[1], category[2], has_image))

        # Load current categories
        load_categories()

        def clear_form():
            """Clear the form fields"""
            nonlocal current_image_path
            category_name_entry.delete(0, tk.END)
            category_discount_entry.delete(0, tk.END)
            category_id_var.set("")
            current_image_path = None
            image_label.config(image="", text="No image selected")
            status_label.config(text="")
            if hasattr(self, 'category_image_photo'):
                delattr(self, 'category_image_photo')

        def on_category_select(event):
            """Handle category selection in treeview"""
            nonlocal current_image_path
            selected_items = category_tree.selection()
            if not selected_items:
                return
                
            # Get selected category data
            item = category_tree.item(selected_items[0])
            category_id = item['values'][0]
            
            # Fetch complete category data
            category = self.category_manager.fetch_category_by_id(category_id)
            if not category:
                return
                
            # Update form with selected category data
            category_id_var.set(category_id)
            category_name_entry.delete(0, tk.END)
            category_name_entry.insert(0, category[1])
            category_discount_entry.delete(0, tk.END)
            category_discount_entry.insert(0, category[2])
            
            # Load category image if available
            current_image_path = category[3]
            load_category_images()
            
            status_label.config(text=f"Editing category: {category[1]}", fg="blue")

        # Bind selection event
        category_tree.bind("<<TreeviewSelect>>", on_category_select)

        def add_category_action():
            """Add a new category"""
            nonlocal current_image_path
            
            try:
                name = category_name_entry.get().strip()
                discount = int(category_discount_entry.get().strip() or "0")
                
                # Validate input
                if not name:
                    status_label.config(text="Category name is required", fg="red")
                    return
                    
                if discount < 0 or discount > 100:
                    status_label.config(text="Discount must be between 0 and 100", fg="red")
                    return
                
                # Process image if selected
                image_path = None
                if current_image_path:
                    # Save image to proper location
                    image_path = self.image_handler.save_product_image(current_image_path, f"category_{name}")
                
                # Add category
                success, message = self.category_manager.add_category(name, discount, image_path)
                
                if success:
                    status_label.config(text=message, fg="green")
                    load_categories()
                    self.display_categories()  # Refresh categories in main view
                    clear_form()
                else:
                    status_label.config(text=message, fg="red")
            except ValueError:
                status_label.config(text="Invalid discount value. Please enter a number.", fg="red")

        def update_category_action():
            """Update an existing category"""
            nonlocal current_image_path
            
            if not category_id_var.get():
                status_label.config(text="No category selected", fg="red")
                return
                
            try:
                category_id = category_id_var.get()
                name = category_name_entry.get().strip()
                discount = int(category_discount_entry.get().strip() or "0")
                
                # Validate input
                if not name:
                    status_label.config(text="Category name is required", fg="red")
                    return
                    
                if discount < 0 or discount > 100:
                    status_label.config(text="Discount must be between 0 and 100", fg="red")
                    return
                
                # Process image if selected or changed
                image_path = None
                category = self.category_manager.fetch_category_by_id(category_id)
                
                if current_image_path:
                    # If current_image_path is different from the one in the database
                    if not category[3] or current_image_path != category[3]:
                        # Save the new image
                        image_path = self.image_handler.save_product_image(current_image_path, f"category_{name}")
                    else:
                        # Keep the same image path
                        image_path = category[3]
                
                # Update category
                success, message = self.category_manager.update_category(category_id, name, discount, image_path)
                
                if success:
                    status_label.config(text=message, fg="green")
                    load_categories()
                    self.display_categories()  # Refresh categories in main view
                else:
                    status_label.config(text=message, fg="red")
            except ValueError:
                status_label.config(text="Invalid discount value. Please enter a number.", fg="red")

        def remove_category_action():
            """Remove the selected category"""
            if not category_id_var.get():
                status_label.config(text="No category selected", fg="red")
                return
                
            category_id = category_id_var.get()
            name = category_name_entry.get()
            
            # Confirm deletion
            if self.confirm(f"Are you sure you want to delete category '{name}'?", "Confirm Deletion"):
                # Get the image path before deleting the category
                category = self.category_manager.fetch_category_by_id(category_id)
                image_path = category[3] if category and len(category) > 3 else None
                
                # Delete the category
                success, message = self.category_manager.delete_category(category_id)
                
                if success:
                    # Delete the image file if it exists
                    if image_path:
                        try:
                            self.image_handler.delete_product_image(image_path)
                        except Exception as e:
                            print(f"Error deleting image: {e}")
                            
                    status_label.config(text=message, fg="green")
                    load_categories()
                    self.display_categories()  # Refresh categories in main view
                    clear_form()
                else:
                    status_label.config(text=message, fg="red")

        # Add actions buttons
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        
        add_button = tk.Button(button_frame, text="Add Category", command=add_category_action, width=12)
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = tk.Button(button_frame, text="Update Category", command=update_category_action, width=12)
        update_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete Category", command=remove_category_action, width=12)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Form", command=clear_form, width=12)
        clear_button.pack(side=tk.LEFT, padx=5)
    
    # Product management windows
    def view_products_window(self):
        """Open window to view all products"""
        view_products_window = tk.Toplevel(self.root)
        view_products_window.title("All Products")  
        view_products_window.attributes("-topmost", True)

        def toggle_checkboxes(changed_var):
            """Toggle checkboxes to ensure only one is selected"""
            if changed_var == "match_case":
                contains_var.set(False)  # Disable "Contains" when "Match Case" is selected
            elif changed_var == "contains":
                match_case_var.set(False)  # Disable "Match Case" when "Contains" is selected

        # Define columns for product treeview
        columns = [
            ("ID", 75, "w"), 
            ("Product Name", 180, "w"), 
            ("Category", 170, "w"), 
            ("Price", 80, "e"), 
            ("Stock", 75, "e"), 
            ("Barcode", 100, "w"), 
            ("Description", 200, "w"), 
            ("Supplier", 150, "w"), 
            ("Discount", 75, "e"), 
            ("UoM", 75, "w"), 
            ("Date Added", 120, "w"), 
            ("Is Alcoholic", 100, "w"), 
            ("Is Active", 100, "w")
        ]

        # Search interface
        tk.Label(view_products_window, text="Search").grid(row=0, column=0, padx=10, pady=10, sticky="NSW")

        search_bar = tk.Entry(view_products_window)
        search_bar.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

        column_combobox = ttk.Combobox(
            view_products_window, 
            values=[col[0] for col in columns], 
            state="readonly"
        )
        column_combobox.grid(row=0, column=2, padx=10, pady=10, sticky="NSEW")
        column_combobox.set("Product Name")  # Default selection

        # Search options
        match_case_var = tk.BooleanVar()
        contains_var = tk.BooleanVar(value=True)  # Default selection

        match_case_check = ttk.Checkbutton(
            view_products_window, 
            text="Match Case", 
            variable=match_case_var, 
            command=lambda: toggle_checkboxes("match_case")
        )
        match_case_check.grid(row=0, column=4, padx=10, pady=10, sticky="NSW")
        
        contains_check = ttk.Checkbutton(
            view_products_window, 
            text="Contains", 
            variable=contains_var, 
            command=lambda: toggle_checkboxes("contains")
        )
        contains_check.grid(row=0, column=4, padx=10, pady=10, sticky="NSE")

        # Create products treeview
        all_products_tree = ttk.Treeview(
            view_products_window, 
            columns=[col[0] for col in columns], 
            show="headings"
        )

        # Configure columns
        for col_name, col_width, col_anchor in columns:
            all_products_tree.heading(col_name, text=col_name)
            all_products_tree.column(col_name, width=col_width, anchor=col_anchor)

        all_products_tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="NSEW")
    
        def display_all_products():
            """Display all products in treeview"""
            all_products_tree.delete(*all_products_tree.get_children())
            products = self.product_manager.fetch_all_products()
            
            if not products:
                all_products_tree.insert("", tk.END, values=("", "", "", "", "", "", "No Products Found"))
            else:
                for product in products:
                    category = self.category_manager.fetch_category_by_id(product[2])
                    supplier = self.supplier_manager.fetch_supplier_by_id(product[7])
                    is_alcoholic = "Yes" if product[11] == 1 else "No"
                    is_active = "Yes" if product[12] == 1 else "No"
                    
                    all_products_tree.insert("", tk.END, values=(
                        product[0], product[1], 
                        category[1] if category else "Unknown", 
                        f"{product[3]:.2f}", product[4], 
                        product[5], product[6], 
                        supplier if supplier else "Unknown", 
                        product[8], product[9], product[10], 
                        is_alcoholic, is_active
                    ))
        
        # Display products
        display_all_products()

        # Refresh button
        view_all_product = tk.Button(
            view_products_window, 
            text="Refresh", 
            command=display_all_products
        )
        view_all_product.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="EW")

        def filter_products():
            """Filter products based on search criteria"""
            all_products_tree.delete(*all_products_tree.get_children())
            
            filter_params = {
                'search_term': search_bar.get(),
                'column': column_combobox.get(),
                'match_case': match_case_var.get(),
                'contains': contains_var.get()
            }
            
            filtered_products = self.product_manager.filter_products(filter_params)
            
            if not filtered_products:
                all_products_tree.insert("", tk.END, values=("", "", "", "", "", "", "No Products Found"))
            else:
                for product in filtered_products:
                    category = self.category_manager.fetch_category_by_id(product[2])
                    supplier = self.supplier_manager.fetch_supplier_by_id(product[7])
                    is_alcoholic = "Yes" if product[11] == 1 else "No"
                    is_active = "Yes" if product[12] == 1 else "No"
                    
                    all_products_tree.insert("", tk.END, values=(
                        product[0], product[1], 
                        category[1] if category else "Unknown", 
                        f"{product[3]:.2f}", product[4], 
                        product[5], product[6], 
                        supplier if supplier else "Unknown", 
                        product[8], product[9], product[10], 
                        is_alcoholic, is_active
                    ))

        # Search button
        tk.Button(
            view_products_window, 
            text="Search", 
            command=filter_products
        ).grid(row=0, column=3, padx=10, pady=10, sticky="NSEW")
    
    def add_product_window(self):
        """Open window to add a new product"""
        new_product_window = tk.Toplevel(self.root)
        new_product_window.title("Add New Product")
        new_product_window.attributes("-topmost", True)

        # Configure grid
        for i in range(2):
            new_product_window.grid_columnconfigure(i, weight=1)
        for i in range(12):
            new_product_window.grid_rowconfigure(i, weight=1)

        # Create form fields with labels
        form_fields = [
            ("Product Name:", None, 0),
            ("Product Price:", validate_price, 1),
            ("Product Stock:", None, 2),
            ("Category:", None, 3, "combobox", [category[1] for category in self.category_manager.fetch_all_categories()]),
            ("Product Barcode:", None, 4),
            ("Description:", None, 5, "multiline"),
            ("Supplier:", None, 7, "combobox", [supplier[1] for supplier in self.supplier_manager.fetch_all_suppliers()]),
            ("Discount:", validate_discount, 8),
            ("Unit of Measurement:", None, 9)
        ]

        # Create entries dictionary to store references
        entries = {}

        # Create form fields
        for field_info in form_fields:
            label_text = field_info[0]
            validator = field_info[1]
            row = field_info[2]
            
            # Create label
            tk.Label(new_product_window, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="W")
            
            # Create appropriate input widget
            if len(field_info) > 3 and field_info[3] == "combobox":
                widget = ttk.Combobox(new_product_window, values=field_info[4], state="readonly")
                widget.grid(row=row, column=1, padx=10, pady=5, sticky="EW")
            elif len(field_info) > 3 and field_info[3] == "multiline":
                widget = tk.Entry(new_product_window)
                widget.grid(row=row, column=1, rowspan=2, padx=10, pady=5, sticky="NSEW")
            else:
                if validator:
                    vcmd = create_validator(new_product_window, validator)
                    widget = tk.Entry(new_product_window, validate="key", validatecommand=vcmd)
                else:
                    widget = tk.Entry(new_product_window)
                widget.grid(row=row, column=1, padx=10, pady=5, sticky="EW")
            
            # Store entry reference
            field_name = label_text.replace(":", "").lower().replace(" ", "_")
            entries[field_name] = widget
            
            # Focus first entry
            if row == 0:
                widget.focus_set()
                
        # Add percent sign for discount
        tk.Label(new_product_window, text="%").grid(row=8, column=1, padx=0, pady=5, sticky="E")
        
        # Checkboxes
        is_alcoholic_var = tk.IntVar()
        is_alcoholic_checkbox = tk.Checkbutton(new_product_window, text="Is Alcoholic", variable=is_alcoholic_var)
        is_alcoholic_checkbox.grid(row=10, column=0, padx=10, pady=5, sticky="W")

        is_active_var = tk.IntVar(value=1)  # Default to active
        is_active_checkbox = tk.Checkbutton(new_product_window, text="Is Active", variable=is_active_var)
        is_active_checkbox.grid(row=10, column=1, padx=10, pady=5, sticky="W")

        # Image selection
        def select_image():
            """Select an image file for the product"""
            self.image_path = filedialog.askopenfilename(
                title="Select Product Image", 
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if self.image_path:
                save_and_display_image(self.image_path)

        def save_and_display_image(image_path):
            """Save and display the selected product image"""
            product_name = entries["product_name"].get()

            if not product_name:
                self.show_error("Please enter the product name first.")
                return

            # Use the image handler to save the image
            self.new_image_path = self.image_handler.save_product_image(image_path, product_name)
            load_image(self.new_image_path)

        def load_image(image_path):
            """Load and display an image"""
            photo = self.image_handler.load_product_image(image_path, size=(100, 100))

            if 'img_label' in new_product_window.children:
                img_label = new_product_window.children['img_label']
                img_label.configure(image=photo)
                img_label.image = photo
            else:
                img_label = tk.Label(new_product_window, image=photo, name='img_label')
                img_label.image = photo
                img_label.grid(row=11, column=0, padx=10, pady=5)

        # Image selection button
        open_image_file = tk.Button(new_product_window, text="Select Image", command=select_image)
        open_image_file.grid(row=11, column=1, padx=10, pady=5, sticky="W")

        # Add product button
        def add_product_action():
            """Add the product to the database"""
            try:
                # Get the category and supplier IDs
                category_name = entries["category"].get()
                supplier_name = entries["supplier"].get()
                
                category_id = self.category_manager.fetch_category_by_name(category_name)
                supplier_id = self.supplier_manager.fetch_supplier_by_name(supplier_name)
                
                if not category_id or not supplier_id:
                    self.show_error("Invalid category or supplier")
                    return
                
                # Prepare product data dictionary
                product_data = {
                    'name': entries["product_name"].get(),
                    'category_id': category_id,
                    'price': float(entries["product_price"].get() or 0),
                    'stock': int(entries["product_stock"].get() or 0),
                    'barcode': entries["product_barcode"].get(),
                    'description': entries["description"].get(),
                    'supplier_id': supplier_id,
                    'discount': int(entries["discount"].get() or 0),
                    'unit_of_measurement': entries["unit_of_measurement"].get(),
                    'image_path': self.new_image_path if hasattr(self, 'new_image_path') else None,
                    'is_alcoholic': is_alcoholic_var.get(),
                    'is_active': is_active_var.get()
                }
                
                # Add product
                success, message = self.product_manager.add_product(product_data)
                
                if success:
                    new_product_window.destroy()
                    self.display_categories()  # Refresh categories in main view
                    self.show_info("Product Added", "Product added successfully.")
                else:
                    self.show_error(message)
                    
            except Exception as e:
                self.show_error(f"Error adding product: {str(e)}")
        
        add_product_button = tk.Button(
            new_product_window, 
            text="Add Product", 
            command=add_product_action
        )
        add_product_button.grid(row=12, columnspan=2, padx=10, pady=10, sticky="NSEW")
    
    def edit_product_window(self):
        """Open window to edit an existing product"""
        edit_product_window = tk.Toplevel(self.root)
        edit_product_window.title("Edit Product")
        edit_product_window.attributes("-topmost", True)

        # Create form fields dictionary to store references
        form_fields = {}

        # Product ID
        tk.Label(edit_product_window, text="Product ID:").grid(row=0, column=0, padx=10, pady=5, sticky="W")
        product_id_entry = tk.Entry(edit_product_window)
        product_id_entry.grid(row=0, column=1, padx=10, pady=5, sticky="EW")
        product_id_entry.focus_set()
        form_fields["product_id"] = product_id_entry

        # Product Name
        tk.Label(edit_product_window, text="Product Name:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
        product_name_entry = tk.Entry(edit_product_window)
        product_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="EW")
        form_fields["product_name"] = product_name_entry

        # Product Price
        tk.Label(edit_product_window, text="Product Price:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
        vcmd = create_validator(edit_product_window, validate_price)
        product_price_entry = tk.Entry(edit_product_window, validate="key", validatecommand=vcmd)
        product_price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="EW")
        form_fields["product_price"] = product_price_entry

        # Product Stock
        tk.Label(edit_product_window, text="Product Stock:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
        product_stock_entry = tk.Entry(edit_product_window)
        product_stock_entry.grid(row=3, column=1, padx=10, pady=5, sticky="EW")
        form_fields["product_stock"] = product_stock_entry

        # Category (Combobox)
        tk.Label(edit_product_window, text="Category:").grid(row=4, column=0, padx=10, pady=5, sticky="W")
        category_combobox = ttk.Combobox(
            edit_product_window, 
            values=[category[1] for category in self.category_manager.fetch_all_categories()], 
            state="readonly"
        )
        category_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="EW")
        form_fields["category"] = category_combobox

        # Barcode
        tk.Label(edit_product_window, text="Product Barcode:").grid(row=5, column=0, padx=10, pady=5, sticky="W")
        product_barcode_entry = tk.Entry(edit_product_window)
        product_barcode_entry.grid(row=5, column=1, padx=10, pady=5, sticky="EW")
        form_fields["product_barcode"] = product_barcode_entry

        # Description
        tk.Label(edit_product_window, text="Description:").grid(row=6, column=0, padx=10, pady=5, sticky="W")
        product_description_entry = tk.Entry(edit_product_window)
        product_description_entry.grid(row=6, column=1, padx=10, pady=5, sticky="EW")
        form_fields["description"] = product_description_entry

        # Supplier (Combobox)
        tk.Label(edit_product_window, text="Supplier:").grid(row=7, column=0, padx=10, pady=5, sticky="W")
        supplier_combobox = ttk.Combobox(
            edit_product_window, 
            values=[supplier[1] for supplier in self.supplier_manager.fetch_all_suppliers()], 
            state="readonly"
        )
        supplier_combobox.grid(row=7, column=1, padx=10, pady=5, sticky="EW")
        form_fields["supplier"] = supplier_combobox

        # Discount
        tk.Label(edit_product_window, text="Discount:").grid(row=8, column=0, padx=10, pady=5, sticky="W")
        product_discount_entry = tk.Entry(edit_product_window)
        product_discount_entry.grid(row=8, column=1, padx=10, pady=5, sticky="EW")
        form_fields["discount"] = product_discount_entry

        # Unit of Measurement
        tk.Label(edit_product_window, text="Unit of Measurement:").grid(row=9, column=0, padx=10, pady=5, sticky="W")
        product_uom_entry = tk.Entry(edit_product_window)
        product_uom_entry.grid(row=9, column=1, padx=10, pady=5, sticky="EW")
        form_fields["unit_of_measurement"] = product_uom_entry

        # Is Alcoholic (Checkbox)
        is_alcoholic_var = tk.IntVar()  
        is_alcoholic_checkbox = tk.Checkbutton(edit_product_window, text="Is Alcoholic", variable=is_alcoholic_var)
        is_alcoholic_checkbox.grid(row=10, column=0, padx=10, pady=5, sticky="W")

        # Is Active (Checkbox)
        is_active_var = tk.IntVar(value=1)  # Default to active
        is_active_checkbox = tk.Checkbutton(edit_product_window, text="Is Active", variable=is_active_var)
        is_active_checkbox.grid(row=10, column=1, padx=10, pady=5, sticky="W")

        # Image Frame
        image_frame = tk.Frame(edit_product_window)
        image_frame.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="NSEW")
        
        # Track current image path
        self.current_product_image = None
        
        def select_image():
            """Select an image file for the product"""
            image_path = filedialog.askopenfilename(
                title="Select Product Image", 
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if image_path:
                load_and_display_image(image_path)
                self.new_image_path = image_path
        
        def load_and_display_image(image_path):
            """Load and display the selected product image"""
            try:
                photo = self.image_handler.load_product_image(image_path, size=(150, 150))
                
                if 'image_label' in locals():
                    image_label.configure(image=photo)
                    image_label.image = photo
                else:
                    image_label = tk.Label(image_frame, image=photo)
                    image_label.image = photo
                    image_label.grid(row=0, column=0, padx=10, pady=5)
            except Exception as e:
                self.show_error(f"Failed to load image: {str(e)}")

        # Image selection button
        select_image_button = tk.Button(image_frame, text="Select New Image", command=select_image)
        select_image_button.grid(row=0, column=1, padx=10, pady=5, sticky="W")
        
        # Image display placeholder
        image_label = tk.Label(image_frame, text="No image selected", width=20, height=10)
        image_label.grid(row=0, column=0, padx=10, pady=5)

        def load_product():
            """Load product data from database based on ID"""
            product_id = product_id_entry.get()
            product = self.product_manager.fetch_product_by_id(int(product_id))
            if product:
                # Update form fields with product data
                product_name_entry.delete(0, tk.END)
                product_name_entry.insert(0, product[1])
            
                category = self.category_manager.fetch_category_by_id(product[2])
                if category:
                    category_combobox.set(category[1])
            
                product_price_entry.delete(0, tk.END)
                product_price_entry.insert(0, product[3])
            
                product_stock_entry.delete(0, tk.END)
                product_stock_entry.insert(0, product[4])

                product_barcode_entry.delete(0, tk.END)
                product_barcode_entry.insert(0, product[5])

                product_description_entry.delete(0, tk.END)
                product_description_entry.insert(0, product[6])

                supplier = self.supplier_manager.fetch_supplier_by_id(product[7])
                if supplier:
                    supplier_combobox.set(supplier)

                product_discount_entry.delete(0, tk.END)
                product_discount_entry.insert(0, product[8])

                product_uom_entry.delete(0, tk.END)
                product_uom_entry.insert(0, product[9])

                is_alcoholic_var.set(product[11])
                is_active_var.set(product[12])
                
                # Load and display product image if available
                if product[13] and os.path.exists(product[13]):
                    load_and_display_image(product[13])
                    self.current_product_image = product[13]
                else:
                    # Clear image if no valid image path
                    image_label.config(image="", text="No image available")
            else:
                self.show_error("Product not found.")

        # Load product button
        tk.Button(edit_product_window, text="Load Product", command=load_product).grid(
            row=12, column=0, padx=10, pady=5, sticky="W"
        )
        
        # Save changes button
        def update_product_action():
            """Update the product in the database"""
            try:
                product_id = product_id_entry.get()
                if not product_id:
                    self.show_error("Please enter a product ID")
                    return
                
                # Get the category and supplier IDs
                category_name = category_combobox.get()
                supplier_name = supplier_combobox.get()
                
                category_id = self.category_manager.fetch_category_by_name(category_name)
                supplier_id = self.supplier_manager.fetch_supplier_by_name(supplier_name)
                
                if not category_id or not supplier_id:
                    self.show_error("Invalid category or supplier")
                    return
                
                # Prepare product data dictionary
                product_data = {
                    'name': product_name_entry.get(),
                    'category_id': category_id,
                    'price': float(product_price_entry.get() or 0),
                    'stock': int(product_stock_entry.get() or 0),
                    'barcode': product_barcode_entry.get(),
                    'description': product_description_entry.get(),
                    'supplier_id': supplier_id,
                    'discount': int(product_discount_entry.get() or 0),
                    'unit_of_measurement': product_uom_entry.get(),
                    'is_alcoholic': is_alcoholic_var.get(),
                    'is_active': is_active_var.get()
                }
                
                # Add image path if provided
                if hasattr(self, 'new_image_path') and self.new_image_path:
                    # Save the new image
                    product_data['image_path'] = self.image_handler.save_product_image(
                        self.new_image_path, 
                        product_data['name']
                    )
                
                # Update product
                success, message = self.product_manager.update_product(int(product_id), product_data)
                
                if success:
                    edit_product_window.destroy()
                    self.display_categories()  # Refresh categories in main view
                    self.show_info("Product Updated", "Product updated successfully.")
                else:
                    self.show_error(message)
                    
            except Exception as e:
                self.show_error(f"Error updating product: {str(e)}")

        save_product_button = tk.Button(
            edit_product_window, 
            text="Save Changes", 
            command=update_product_action
        )
        save_product_button.grid(row=12, column=1, padx=10, pady=5, sticky="E")
    
    def remove_product_window(self):
        """Open window to remove a product"""
        remove_product_window = tk.Toplevel(self.root)
        remove_product_window.title("Remove a Product")
        remove_product_window.resizable(False, False)
        remove_product_window.attributes("-topmost", True)

        # Configure grid
        for i in range(2):
            remove_product_window.grid_columnconfigure(i, weight=1)
        for i in range(3):
            remove_product_window.grid_rowconfigure(i, weight=1)
    
        # Product ID entry
        tk.Label(remove_product_window, text="Product ID:").grid(row=0, column=0, padx=10, pady=5)
        product_id_entry = tk.Entry(remove_product_window)
        product_id_entry.grid(row=0, column=1, padx=10, pady=5)
    
        # Remove button
        def remove_product_action():
            """Remove the product from the database"""
            product_id = product_id_entry.get()
            
            if not product_id:
                self.show_error("No product ID provided.")
                return
                
            # Get product details first to show confirmation
            product = self.product_manager.fetch_product_by_id(int(product_id))
            
            if product:
                result = self.confirm(
                    f"Are you sure you would like to remove: {product[1]}?", 
                    "Product Removal"
                )
                if result:
                    success, message = self.product_manager.delete_product(int(product_id))
                    
                    if success:
                        remove_product_window.destroy()
                        self.display_categories()  # Refresh categories in main view
                        self.show_info("Product Removed", "Product removed successfully.")
                    else:
                        self.show_error(message)
                else:
                    self.show_info("Cancelled", "Product removal cancelled.")
            else:  
                self.show_error("Product not found.")
    
        tk.Button(
            remove_product_window, 
            text="Remove Product", 
            command=remove_product_action
        ).grid(row=1, columnspan=2, padx=10, pady=10)
    
    def update_stock_window(self):
        """Open window to update product stock"""
        stock_update_window = tk.Toplevel(self.root)
        stock_update_window.title("Update Stock")
        stock_update_window.resizable(False, False)
        stock_update_window.attributes("-topmost", True)

        # New stock entry
        tk.Label(stock_update_window, text="New Stock:").grid(row=0, column=0, padx=10, pady=5)
        stock_entry = tk.Entry(stock_update_window)
        stock_entry.grid(row=0, column=1, padx=10, pady=5)

        # Product ID entry
        tk.Label(stock_update_window, text="Product ID:").grid(row=1, column=0, padx=10, pady=5)
        stock_id_entry = tk.Entry(stock_update_window)
        stock_id_entry.grid(row=1, column=1, padx=10, pady=5)

        # Update button
        def update_stock_action():
            """Update stock quantity"""
            try:
                product_id = int(stock_id_entry.get())
                new_stock = int(stock_entry.get())
                
                success, message = self.product_manager.update_stock(product_id, new_stock)
                
                if success:
                    self.show_info("Stock Updated", "Stock updated successfully")
                    stock_update_window.destroy()
                else:
                    self.show_error(message)
            except ValueError:
                self.show_error("Invalid quantity or product ID.")
        
        tk.Button(
            stock_update_window, 
            text="Update Stock", 
            command=update_stock_action
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="NSEW")
    
    # Placeholder methods for menu items - implement these later
    def manage_users_window(self):
        manage_users_window = tk.Toplevel(self.root)
        manage_users_window.title("Manage Users")
        manage_users_window.attributes("-topmost", True)

        # Create left panel for user list
        left_panel = tk.Frame(manage_users_window, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create right panel for user details
        right_panel = tk.Frame(manage_users_window)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add title label
        tk.Label(right_panel, text="User Details", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="W", pady=(0, 10)
        )

        # User form fields
        tk.Label(right_panel, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
        username_entry = tk.Entry(right_panel, width=25)
        username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="W")

        tk.Label(right_panel, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
        password_entry = tk.Entry(right_panel, show="*", width=25)
        password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="W")

        tk.Label(right_panel, text="Confirm Password:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
        confirm_password_entry = tk.Entry(right_panel, show="*", width=25)
        confirm_password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="W")

        tk.Label(right_panel, text="Role:").grid(row=4, column=0, padx=10, pady=5, sticky="W")
        
        # Get roles from database
        roles = self.role_manager.get_all_roles()
        role_ids = {role[1]: role[0] for role in roles}
        role_names = [role[1] for role in roles]

        role_combobox = ttk.Combobox(right_panel, values=role_names, state="readonly", width=23)
        role_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="W")
        if role_names:
            role_combobox.current(0)  # Select the first role by default

        # Add status indicator
        status_label = tk.Label(right_panel, text="", font=("Segoe UI", 10))
        status_label.grid(row=8, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="W")

        # Create user treeview
        columns = ("ID", "Username", "Role")
        users_tree = ttk.Treeview(left_panel, columns=columns, show="headings", height=15)
        
        # Configure columns
        users_tree.heading("ID", text="ID")
        users_tree.heading("Username", text="Username")
        users_tree.heading("Role", text="Role")
        
        users_tree.column("ID", width=50, anchor="w")
        users_tree.column("Username", width=150, anchor="w")
        users_tree.column("Role", width=120, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=users_tree.yview)
        users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Track selected user ID
        selected_user_id = tk.StringVar()
        
        # Clear form fields
        def clear_form():
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            confirm_password_entry.delete(0, tk.END)
            if role_names:
                role_combobox.current(0)
            selected_user_id.set("")
            status_label.config(text="")
            
        # Functions for user management
        def add_user_action():
            """Add a new user"""
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_password_entry.get()
            role_name = role_combobox.get()
            role_id = role_ids.get(role_name)
            
            # Validate input
            if not username or not password:
                status_label.config(text="Username and password are required", fg="red")
                return
                
            if password != confirm:
                status_label.config(text="Passwords do not match", fg="red")
                return
                
            if not role_id:
                status_label.config(text="Please select a role", fg="red")
                return
                
            success, message = self.user_manager.add_user(username, password, role_id)
            
            if success:
                status_label.config(text=f"User '{username}' added successfully", fg="green")
                refresh_users_list()
                clear_form()
            else:
                status_label.config(text=message, fg="red")

        def update_user_action():
            """Update an existing user"""
            if not selected_user_id.get():
                status_label.config(text="No user selected", fg="red")
                return
                
            user_id = selected_user_id.get()
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_password_entry.get()
            role_name = role_combobox.get()
            role_id = role_ids.get(role_name)
            
            # Validate input
            if not username:
                status_label.config(text="Username is required", fg="red")
                return
                
            if password and password != confirm:
                status_label.config(text="Passwords do not match", fg="red")
                return
                
            if not role_id:
                status_label.config(text="Please select a role", fg="red")
                return
                
            success, message = self.user_manager.update_user(user_id, username, password, role_id)
            
            if success:
                status_label.config(text=f"User '{username}' updated successfully", fg="green")
                refresh_users_list()
            else:
                status_label.config(text=message, fg="red")

        def delete_user_action():
            """Delete a user"""
            if not selected_user_id.get():
                status_label.config(text="No user selected", fg="red")
                return
                
            username = username_entry.get()
            
            # Confirm deletion
            confirm = self.confirm(
                f"Are you sure you want to delete user '{username}'?", 
                "Confirm Deletion"
            )
            
            if confirm:
                success, message = self.user_manager.delete_user(username)
                
                if success:
                    status_label.config(text=message, fg="green")
                    refresh_users_list()
                    clear_form()
                else:
                    status_label.config(text=message, fg="red")

        def on_user_select(event):
            """Handle user selection in treeview"""
            selected_items = users_tree.selection()
            if not selected_items:
                return
                
            # Get selected user data
            item = users_tree.item(selected_items[0])
            user_id = item['values'][0]
            username = item['values'][1]
            role_name = item['values'][2]
            
            # Update form with selected user data
            selected_user_id.set(user_id)
            username_entry.delete(0, tk.END)
            username_entry.insert(0, username)
            password_entry.delete(0, tk.END)
            confirm_password_entry.delete(0, tk.END)
            
            # Set selected role
            if role_name in role_names:
                role_combobox.set(role_name)
            
            status_label.config(text=f"Editing user: {username}", fg="blue")

        # Function to refresh users list
        def refresh_users_list():
            """Refresh the users list in the treeview"""
            users_tree.delete(*users_tree.get_children())
            
            users = self.user_manager.get_all_users()
            
            if not users:
                users_tree.insert("", tk.END, values=("--", "No users found", "--"))
            else:
                for user in users:
                    users_tree.insert("", tk.END, values=(user[0], user[1], user[4]))  # ID, Username, Role Name

        # Bind user selection event
        users_tree.bind("<<TreeviewSelect>>", on_user_select)

        # Add action buttons
        button_frame = tk.Frame(right_panel)
        button_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="EW")
        
        add_button = tk.Button(button_frame, text="Add New User", command=add_user_action, width=12)
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = tk.Button(button_frame, text="Update User", command=update_user_action, width=12)
        update_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete User", command=delete_user_action, width=12)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Form", command=clear_form, width=12)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Initialize by loading users
        refresh_users_list()
        
    def manage_roles_window(self):
        """Open window to manage user roles"""
        roles_window = tk.Toplevel(self.root)
        roles_window.title("Manage Roles")
        roles_window.attributes("-topmost", True)
        
        # Create frames
        list_frame = tk.Frame(roles_window)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_frame = tk.Frame(roles_window)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create role list
        tk.Label(list_frame, text="Roles", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Role treeview
        columns = ("ID", "Role Name", "User Count")
        roles_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        roles_tree.heading("ID", text="ID")
        roles_tree.heading("Role Name", text="Role Name")
        roles_tree.heading("User Count", text="Users")
        
        roles_tree.column("ID", width=50, anchor="w")
        roles_tree.column("Role Name", width=150, anchor="w")
        roles_tree.column("User Count", width=50, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=roles_tree.yview)
        roles_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        roles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Role details form
        tk.Label(details_frame, text="Role Details", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        
        # Role ID (hidden)
        role_id_var = tk.StringVar()
        
        # Role name
        tk.Label(details_frame, text="Role Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        role_name_entry = tk.Entry(details_frame, width=25)
        role_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Status indicator
        status_label = tk.Label(details_frame, text="", font=("Segoe UI", 10))
        status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")
        
        # Refresh role list
        def refresh_roles_list():
            roles_tree.delete(*roles_tree.get_children())
            
            # Get all roles
            roles = self.role_manager.get_all_roles()
            
            for role in roles:
                role_id = role[0]
                
                # Count users with this role_id
                user_count = 0
                all_users = self.user_manager.get_all_users()
                for user in all_users:
                    if user[3] == role_id:  # role_id is at index 3
                        user_count += 1
                
                roles_tree.insert("", tk.END, values=(role_id, role[1], user_count))
                
            if not roles:
                roles_tree.insert("", tk.END, values=("--", "No roles found", "--"))
        
        # Clear form
        def clear_form():
            role_name_entry.delete(0, tk.END)
            role_id_var.set("")
            status_label.config(text="")
            
        # Handle role selection
        def on_role_select(event):
            selected_items = roles_tree.selection()
            if not selected_items:
                return
                
            # Get selected role data
            item = roles_tree.item(selected_items[0])
            role_id = item['values'][0]
            role_name = item['values'][1]
            
            # Update form with selected role data
            role_id_var.set(role_id)
            role_name_entry.delete(0, tk.END)
            role_name_entry.insert(0, role_name)
            
            status_label.config(text=f"Editing role: {role_name}", fg="blue")
        
        # Add role
        def add_role_action():
            role_name = role_name_entry.get().strip()
            
            # Validate input
            if not role_name:
                status_label.config(text="Role name is required", fg="red")
                return
                
            # Add role
            success, message = self.role_manager.add_role(role_name)
            
            if success:
                status_label.config(text=message, fg="green")
                refresh_roles_list()
                clear_form()
            else:
                status_label.config(text=message, fg="red")
        
        # Update role
        def update_role_action():
            if not role_id_var.get():
                status_label.config(text="No role selected", fg="red")
                return
                
            role_id = role_id_var.get()
            new_role_name = role_name_entry.get().strip()
            
            # Validate input
            if not new_role_name:
                status_label.config(text="Role name is required", fg="red")
                return
                
            # Update role
            success, message = self.role_manager.update_role(role_id, new_role_name)
            
            if success:
                status_label.config(text=message, fg="green")
                refresh_roles_list()
            else:
                status_label.config(text=message, fg="red")
        
        # Delete role
        def delete_role_action():
            if not role_id_var.get():
                status_label.config(text="No role selected", fg="red")
                return
                
            role_id = role_id_var.get()
            role_name = role_name_entry.get()
            
            # Confirm deletion
            confirm = self.confirm(
                f"Are you sure you want to delete role '{role_name}'?", 
                "Confirm Deletion"
            )
            
            if confirm:
                # Delete role
                success, message = self.role_manager.delete_role(role_id)
                
                if success:
                    status_label.config(text=message, fg="green")
                    refresh_roles_list()
                    clear_form()
                else:
                    status_label.config(text=message, fg="red")
        
        # Bind selection event
        roles_tree.bind("<<TreeviewSelect>>", on_role_select)
        
        # Add action buttons
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        
        add_button = tk.Button(button_frame, text="Add Role", command=add_role_action, width=10)
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = tk.Button(button_frame, text="Update Role", command=update_role_action, width=10)
        update_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete Role", command=delete_role_action, width=10)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Form", command=clear_form, width=10)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Initialize by loading roles
        refresh_roles_list()
        
    def monthly_profit_window(self):
        """Open window to view monthly profit reports"""
        report_window = tk.Toplevel(self.root)
        report_window.title("Monthly Profit Report")
        report_window.resizable(False, False)
        report_window.attributes("-topmost", True)

        # Month selection
        month_label = tk.Label(report_window, text="Month:")
        month_label.grid(row=0, column=0, padx=10, pady=5)

        from calendar import month_name
        month_names = list(month_name)[1:]
        month_combobox = ttk.Combobox(report_window, values=month_names, state="readonly")
        month_combobox.grid(row=0, column=1, padx=10, pady=5)
        month_combobox.current(datetime.now().month - 1)  # Default to current month

        # Year selection
        year_label = tk.Label(report_window, text="Year:")
        year_label.grid(row=1, column=0, padx=10, pady=5)

        year_combobox = ttk.Combobox(
            report_window, 
            values=list(range(2000, datetime.now().year + 1)), 
            state="readonly"
        )
        year_combobox.grid(row=1, column=1, padx=10, pady=5)
        year_combobox.current(datetime.now().year - 2000)  # Default to current year

        # Report display
        report_label = tk.Label(report_window, text="")
        report_label.grid(row=3, columnspan=2, padx=10, pady=10)

        # Generate button
        def generate_report():
            month_idx = month_names.index(month_combobox.get()) + 1
            year = int(year_combobox.get())
            
            # Use the report manager to get monthly sales
            total_sales = self.report_manager.fetch_monthly_sales(month_idx, year)
            report_label.config(text=f"Total Sales for {month_combobox.get()}/{year}: ${total_sales:.2f}")
            
        generate_button = tk.Button(
            report_window, 
            text="Generate Report", 
            command=generate_report
        )
        generate_button.grid(row=2, columnspan=2, padx=10, pady=10)
        
    def sales_history_window(self):
        """Open window to view sales history"""
        sales_history_window = tk.Toplevel(self.root)
        sales_history_window.title("Sales History")  
        sales_history_window.resizable(False, False)
        sales_history_window.attributes("-topmost", True)

        # Transaction ID list frame
        transaction_frame = tk.Frame(sales_history_window)
        transaction_frame.grid(row=0, column=0, padx=10, pady=5, sticky="NS")

        # Sales details treeview
        sales_tree = ttk.Treeview(
            sales_history_window, 
            columns=("ID", "Product Name", "Quantity", "Total", "Discount", "Timestamp"), 
            height=10, 
            show="headings"
        )
        sales_tree.heading("ID", text="ID")
        sales_tree.heading("Product Name", text="Product Name")
        sales_tree.heading("Quantity", text="Quantity")
        sales_tree.heading("Total", text="Total")
        sales_tree.heading("Discount", text="Discount")
        sales_tree.heading("Timestamp", text="Timestamp")
        sales_tree.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky="EW")

        # Total amount and cash given labels
        total_label = tk.Label(sales_history_window, text="$0.00")
        total_label.grid(row=1, column=1, padx=10, pady=5, sticky="E")

        cash_given_label = tk.Label(sales_history_window, text="$0.00")
        cash_given_label.grid(row=1, column=2, padx=10, pady=5, sticky="EE")

        def display_transaction_ids():
            """Display all transaction IDs in a frame"""
            # Clear existing widgets
            for widget in transaction_frame.winfo_children():
                widget.destroy()

            # Get all transaction IDs
            transactions = self.transaction_manager.fetch_transaction_history()

            if not transactions:
                tk.Label(transaction_frame, text="No sales records found").grid(row=0, column=0)
            else:
                # Create a button for each transaction
                for idx, transaction_id in enumerate(transactions):
                    row = idx + 1
                    
                    button = tk.Button(
                        transaction_frame, 
                        text=transaction_id, 
                        command=lambda tid=transaction_id: display_sales_history(tid)
                    )
                    button.grid(row=row, column=0, padx=5, pady=2, sticky="EW")

        def display_sales_history(transaction_id):
            """Display sale details for a specific transaction"""
            sales_tree.delete(*sales_tree.get_children())

            # Get transaction details
            sales = self.transaction_manager.fetch_transaction_details(transaction_id)
            
            if not sales:
                sales_tree.insert("", tk.END, values=("No products found for this transaction", "", "", "", "", ""))
            else:
                for sale in sales:
                    sales_tree.insert("", tk.END, values=(
                        sale['id'], 
                        sale['product_name'],
                        sale['quantity'],
                        f"{sale['total']:.2f}",
                        sale['discount'],
                        sale['timestamp']
                    ))

        # Refresh button
        refresh_button = tk.Button(
            sales_history_window, 
            text="Refresh", 
            command=display_transaction_ids
        )
        refresh_button.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="EW")

        # Display initial transaction IDs
        display_transaction_ids()

    def manage_suppliers_window(self):
        """Open window to manage suppliers"""
        suppliers_window = tk.Toplevel(self.root)
        suppliers_window.title("Manage Suppliers")
        suppliers_window.attributes("-topmost", True)

        # Create split layout
        list_frame = tk.Frame(suppliers_window)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_frame = tk.Frame(suppliers_window)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create supplier list with treeview
        tk.Label(list_frame, text="Suppliers", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        columns = ("ID", "Name", "Contact Info", "Products")
        suppliers_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        suppliers_tree.heading("ID", text="ID")
        suppliers_tree.heading("Name", text="Supplier Name")
        suppliers_tree.heading("Contact Info", text="Contact Info")
        suppliers_tree.heading("Products", text="Products")
        
        suppliers_tree.column("ID", width=50, anchor="w")
        suppliers_tree.column("Name", width=150, anchor="w")
        suppliers_tree.column("Contact Info", width=200, anchor="w")
        suppliers_tree.column("Products", width=70, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=suppliers_tree.yview)
        suppliers_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Supplier details form
        tk.Label(details_frame, text="Supplier Details", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        
        # Supplier ID (hidden)
        supplier_id_var = tk.StringVar()
        
        # Supplier name
        tk.Label(details_frame, text="Supplier Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        supplier_name_entry = tk.Entry(details_frame, width=30)
        supplier_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Contact information
        tk.Label(details_frame, text="Contact Information:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        contact_info_text = tk.Text(details_frame, width=30, height=5)
        contact_info_text.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Status indicator
        status_label = tk.Label(details_frame, text="", font=("Segoe UI", 10))
        status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")
        
        # Refresh supplier list
        def refresh_suppliers_list():
            suppliers_tree.delete(*suppliers_tree.get_children())
            
            # Get all suppliers using the SupplierManager
            suppliers = self.supplier_manager.fetch_all_suppliers()
            
            # Get all products once to avoid multiple database calls
            all_products = self.product_manager.fetch_all_products()
            
            for supplier in suppliers:
                supplier_id = supplier[0]
                
                # Count products for this supplier
                product_count = 0
                for product in all_products:
                    if product[7] == supplier_id:  # Check if product's supplier_id matches
                        product_count += 1

                suppliers_tree.insert("", tk.END, values=(supplier_id, supplier[1], supplier[2], product_count))
                
            if not suppliers:
                suppliers_tree.insert("", tk.END, values=("--", "No Suppliers found", "--"))
        
        # Clear form
        def clear_form():
            supplier_name_entry.delete(0, tk.END)
            contact_info_text.delete("1.0", tk.END)
            supplier_id_var.set("")
            status_label.config(text="")
            
        # Handle supplier selection
        def on_supplier_select(event):
            selected_items = suppliers_tree.selection()
            if not selected_items:
                return
                
            # Get selected supplier data
            item = suppliers_tree.item(selected_items[0])
            supplier_id = item['values'][0]
            
            # Skip if this is the "No suppliers found" placeholder
            if supplier_id == "--":
                return
                
            # Update form with selected supplier data
            supplier_id_var.set(supplier_id)
            
            # Get the supplier name and contact info from the tree view
            supplier_name = item['values'][1]
            contact_info = item['values'][2]
            
            supplier_name_entry.delete(0, tk.END)
            supplier_name_entry.insert(0, supplier_name)
            contact_info_text.delete("1.0", tk.END)
            contact_info_text.insert("1.0", contact_info if contact_info else "")
            
            status_label.config(text=f"Editing supplier: {supplier_name}", fg="blue")
        
        # Add supplier
        def add_supplier_action():
            name = supplier_name_entry.get().strip()
            contact_info = contact_info_text.get("1.0", tk.END).strip()
            
            # Validate input
            if not name:
                status_label.config(text="Supplier name is required", fg="red")
                return
                
            # Add supplier using the SupplierManager
            success, message = self.supplier_manager.add_supplier(name, contact_info)
            
            if success:
                status_label.config(text=message, fg="green")
                refresh_suppliers_list()
                clear_form()
            else:
                status_label.config(text=message, fg="red")
        
        # Update supplier
        def update_supplier_action():
            if not supplier_id_var.get():
                status_label.config(text="No supplier selected", fg="red")
                return
                
            supplier_id = supplier_id_var.get()
            name = supplier_name_entry.get().strip()
            contact_info = contact_info_text.get("1.0", tk.END).strip()
            
            # Validate input
            if not name:
                status_label.config(text="Supplier name is required", fg="red")
                return
                
            # Update supplier using the SupplierManager
            success, message = self.supplier_manager.update_supplier(supplier_id, name, contact_info)
            
            if success:
                status_label.config(text=message, fg="green")
                refresh_suppliers_list()
            else:
                status_label.config(text=message, fg="red")
        
        # Delete supplier
        def delete_supplier_action():
            if not supplier_id_var.get():
                status_label.config(text="No supplier selected", fg="red")
                return
                
            supplier_id = supplier_id_var.get()
            name = supplier_name_entry.get()
            
            # Confirm deletion
            confirm = self.confirm(
                f"Are you sure you want to delete supplier '{name}'?", 
                "Confirm Deletion"
            )
            
            if confirm:
                # Delete supplier using the SupplierManager
                success, message = self.supplier_manager.delete_supplier(supplier_id)
                
                if success:
                    status_label.config(text=message, fg="green")
                    refresh_suppliers_list()
                    clear_form()
                else:
                    status_label.config(text=message, fg="red")
        
        # Bind selection event
        suppliers_tree.bind("<<TreeviewSelect>>", on_supplier_select)
        
        # Add action buttons
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="ew")
        
        add_button = tk.Button(button_frame, text="Add Supplier", command=add_supplier_action, width=12)
        add_button.pack(side=tk.LEFT, padx=5)
        
        update_button = tk.Button(button_frame, text="Update Supplier", command=update_supplier_action, width=12)
        update_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete Supplier", command=delete_supplier_action, width=12)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Form", command=clear_form, width=12)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Initialize by loading suppliers
        refresh_suppliers_list()