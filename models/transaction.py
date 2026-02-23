"""
Transaction Management Module
Handles sales transactions.
"""

import uuid
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager
from models.product import ProductManager
from models.category import CategoryManager#

from models.reciept import ReceiptHandler

import uuid
from typing import List, Tuple, Optional, Dict, Any

class TransactionManager:
    """Manages sales transactions."""
    
    def __init__(self):
        """Initialize the transaction manager."""
        self.db_manager = get_db_manager()
        self.product_manager = ProductManager()
        self.category_manager = CategoryManager()
        self.receipt_handler = ReceiptHandler(self.db_manager)
        
        # Current transaction state
        self.selected_products = []
    
    def clear_transaction(self) -> None:
        """Clear the current transaction."""
        self.selected_products = []
    
    def get_transaction_products(self) -> List[Tuple]:
        """Get the products in the current transaction.
        
        Returns:
            List of product tuples: (iid, barcode, name, quantity, price, discount)
        """
        return self.selected_products
    
    def alter_quantity(self, item_id: str, new_quantity: int) -> Tuple[bool, str]:
        """Change the quantity of a selected product in the transaction.
        
        Args:
            item_id: The unique ID of the transaction item
            new_quantity: The new quantity
            
        Returns:
            Tuple containing success status and message
        """
        if new_quantity <= 0:
            return False, "Invalid quantity provided"
        
        # Find the product in the transaction
        for i, product in enumerate(self.selected_products):
            if product[0] == item_id:
                # Get unit price
                unit_price = float(product[4]) / int(product[3])
                new_price = unit_price * int(new_quantity)
                
                # Update product in list
                self.selected_products[i] = (
                    product[0],             # UUID
                    product[1],             # Barcode
                    product[2],             # Name
                    int(new_quantity),      # New quantity
                    round(new_price, 2),    # New total price
                    product[5]              # Discount percentage
                )
                return True, f"Quantity updated to {new_quantity}"
        
        return False, "Please select a product"
    
    def apply_discount(self, item_id: str, discount_percent: float) -> Tuple[bool, str]:
        """Apply a discount to a selected item in the transaction.
        
        Args:
            item_id: The unique ID of the transaction item
            discount_percent: Discount percentage to apply
            
        Returns:
            Tuple containing success status and message
        """
        # Validate discount percentage
        try:
            discount_percent = float(discount_percent)
            if discount_percent < 0 or discount_percent > 100:
                return False, "Invalid discount provided. Must be between 0 and 100."
        except ValueError:
            return False, "Invalid discount provided"
        
        # Find the product in the transaction
        for i, product in enumerate(self.selected_products):
            if product[0] == item_id:
                # Retrieve the original product price from the database
                barcode = product[1]
                original_product = self.product_manager.fetch_product_by_barcode(barcode)
                
                if not original_product:
                    return False, "Error: Could not find original product price"
                    
                # Get original price and apply any category discount
                original_price = original_product[3]
                category = self.category_manager.fetch_category_by_id(original_product[2])
                category_discount = category[2] if category else 0
                
                # Calculate final price with both category and item discounts
                total_discount_percent = category_discount + discount_percent
                discount_multiplier = (100 - total_discount_percent) / 100
                new_unit_price = round(original_price * discount_multiplier, 2)

                if new_unit_price < 0.01: # Prevents item's costing 0.00
                    new_unit_price = 0.01
                
                # Update product in list
                self.selected_products[i] = (
                    product[0],                                # UUID
                    product[1],                                # Barcode
                    product[2],                                # Product name
                    product[3],                                # Quantity
                    round(new_unit_price * int(product[3]), 2), # New total price
                    discount_percent                           # Discount percentage
                )
                return True, f"Discount of {discount_percent}% applied"
        
        return False, "Please select a product"
    
    def remove_product(self, item_id: str) -> Tuple[bool, str]:
        """Remove a product from the transaction.
        
        Args:
            item_id: The unique ID of the transaction item
            
        Returns:
            Tuple containing success status and message
        """
        # Find and remove the product
        for i, product in enumerate(self.selected_products):
            if product[0] == item_id:
                del self.selected_products[i]
                return True, f"Product removed"
        
        return False, "Please select a product"
    
    def calculate_total(self) -> float:
        """Calculate the total cost of the current transaction.
        
        Returns:
            The total cost
        """
        total = 0.0
        for product in self.selected_products:
            total += float(product[4])  # Add product price
        return round(total, 2)
    
    def add_product_to_transaction(self, product_id: Optional[int] = None, 
                                  product_barcode: Optional[str] = None) -> Tuple[bool, str, Optional[Tuple]]:
        """Add a product to the current transaction.
        
        Args:
            product_id: Optional product ID
            product_barcode: Optional product barcode
            
        Returns:
            Tuple containing (success, message, added_product_data)
            added_product_data is a tuple (iid, barcode, name, quantity, price, discount)
        """
        # Fetch product by ID or barcode
        if product_id:
            product = self.product_manager.fetch_product_by_id(product_id)
        elif product_barcode:
            product = self.product_manager.fetch_product_by_barcode(product_barcode)
        else:
            return False, "No product ID or barcode provided", None
        
        if not product:
            return False, "Product not found", None
        
        # Calculate price with discounts
        category = self.category_manager.fetch_category_by_id(product[2])
        
        if category:
            product_category_discount = category[2]
        else:
            product_category_discount = 0
            
        total_discount_percent = product_category_discount + product[8]
        discount = (total_discount_percent / 100) * product[3]
        new_price = round(product[3] - discount, 2)
        
        # Generate unique ID for the transaction item
        unique_iid = str(uuid.uuid4())
        
        # Create transaction item
        transaction_item = (
            unique_iid,        # Unique ID
            product[5],        # Barcode
            product[1],        # Name
            1,                 # Quantity
            new_price,         # Price
            total_discount_percent  # Discount
        )
        
        # Add to selected products
        self.selected_products.append(transaction_item)
        
        # Check if product is out of stock (message only, still add)
        message = ""
        if product[4] < 1:  # Stock check
            message = "Not enough stock"
            
        return True, message, transaction_item
        
    def complete_sale(self, payment_amount: float, username: str) -> Tuple[bool, str, float, str]:
        """Complete a sale by recording it in the database.
        
        Args:
            payment_amount: Amount of payment received
            
        Returns:
            Tuple containing (success, message, change_amount)
        """
        try:
            # Calculate total
            total_amount = self.calculate_total()
            
            # Validate payment amount
            if payment_amount < total_amount:
                return False, "Payment amount is less than the total", 0.00, ""
            
            # Calculate change
            change = payment_amount - total_amount
            
            # Generate a transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Record each product in the sale
            for product in self.selected_products:
                # Get product ID from barcode
                product_db = self.product_manager.fetch_product_by_barcode(product[1])
                
                if product_db:
                    product_id = product_db[0]
                    
                    # Update stock
                    current_stock = product_db[4]
                    new_stock = max(0, current_stock - product[3])
                    self.product_manager.update_stock(product_id, new_stock)
                    
                    # Record sale
                    self.db_manager.pos_db.execute("""
                        INSERT INTO sales (transaction_id, product_id, quantity, total, discount) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (transaction_id, product_id, product[3], product[4], product[5]))
            
            # Commit changes
            self.db_manager.commit_pos()
            
            # Generate receipt
            receipt_content = self.receipt_handler.generate_receipt_content(
                transaction_id, 
                username, 
                payment_amount
            )
            
            # Display receipt
            self.receipt_handler.display_receipt(receipt_content, transaction_id)
            
            # Clear transaction
            self.clear_transaction()
            
            return True, "Sale completed successfully", change, ""
        except Exception as e:
            return False, f"Error completing sale: {str(e)}", 0.0, ""
    
    def fetch_transaction_history(self) -> List[str]:
        """Retrieve all transaction IDs from the sales history.
        
        Returns:
            List of transaction IDs
        """
        self.db_manager.pos_db.execute("SELECT DISTINCT transaction_id FROM sales")
        transactions = self.db_manager.pos_db.fetchall()
        return [t[0] for t in transactions]
    
    def fetch_transaction_details(self, transaction_id: str) -> List[Dict[str, Any]]:
        """Retrieve sale details for a specific transaction.
        
        Args:
            transaction_id: ID of the transaction to retrieve
            
        Returns:
            List of dictionaries containing sale details
        """
        self.db_manager.pos_db.execute("SELECT * FROM sales WHERE transaction_id = ?", (transaction_id,))
        sales = self.db_manager.pos_db.fetchall()
        
        result = []
        for sale in sales:
            # Get product name
            product = self.product_manager.fetch_product_by_id(sale[2])
            product_name = product[1] if product else "Product Not Found"
            
            # Format the result
            result.append({
                'id': sale[0],
                'product_name': product_name,
                'quantity': sale[3],
                'total': sale[4],
                'discount': sale[5],
                'timestamp': sale[6]
            })
        
        return result 