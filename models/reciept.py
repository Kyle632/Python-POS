"""
Receipt Handler Module
Handles the generation and printing of transaction receipts.
"""

import os
import datetime
from tkinter import filedialog, messagebox
import tkinter as tk

class ReceiptHandler:
    """Manages receipt generation and printing for transactions."""
    
    def __init__(self, db_manager, company_name="My Store"):
        """Initialize the receipt handler.
        
        Args:
            db_manager: Database manager instance to access transaction data
            company_name: Name of the store/company to display on receipts
        """
        self.db_manager = db_manager
        self.company_name = company_name
        self.receipt_dir = "receipts"
        
        # Create receipts directory if it doesn't exist
        os.makedirs(self.receipt_dir, exist_ok=True)
    
    def generate_receipt_content(self, transaction_id, cashier_name, payment_amount, payment_method="Cash"):
        """Generate formatted content for a receipt.
        
        Args:
            transaction_id: ID of the transaction
            cashier_name: Name of the cashier who processed the transaction
            payment_amount: Amount paid by customer
            payment_method: Method of payment (default: Cash)
            
        Returns:
            Formatted receipt content as a string
        """
        # Get transaction details from the database
        transaction_details = self._get_transaction_details(transaction_id)
        if not transaction_details:
            return "Error: Transaction not found"
        
        # Calculate totals
        subtotal = sum(item['total'] for item in transaction_details)
        change = payment_amount - subtotal
        
        # Format the receipt
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        receipt = []
        receipt.append(f"{self.company_name}".center(40))
        receipt.append(f"".center(40, '-'))
        receipt.append(f"Receipt #{transaction_id}")
        receipt.append(f"Date: {current_time}")
        receipt.append(f"Cashier: {cashier_name}")
        receipt.append(f"".center(40, '-'))
        
        # Add items
        receipt.append(f"{'Item':<20}{'Qty':^5}{'Price':^8}{'Total':>7}")
        receipt.append(f"".center(40, '-'))
        
        for item in transaction_details:
            name = item['name']
            if len(name) > 18:
                name = name[:15] + "..."
            
            receipt.append(f"{name:<20}{item['quantity']:^5}{item['price']:^8.2f}{item['total']:>7.2f}")
        
        receipt.append(f"".center(40, '-'))
        receipt.append(f"{'Subtotal:':<30}{subtotal:>10.2f}")
        if transaction_details[0].get('discount') and transaction_details[0].get('discount') > 0:
            discount = transaction_details[0].get('discount')
            receipt.append(f"{'Discount:':<30}{discount:>10.2f}")
            subtotal -= discount
        
        receipt.append(f"{'Total:':<30}{subtotal:>10.2f}")
        receipt.append(f"{'Payment ({payment_method}):':<30}{payment_amount:>10.2f}")
        receipt.append(f"{'Change:':<30}{change:>10.2f}")
        receipt.append(f"".center(40, '-'))
        receipt.append("Thank you for your purchase!")
        receipt.append(f"".center(40, '-'))
        
        return "\n".join(receipt)
    
    def _get_transaction_details(self, transaction_id):
        """Retrieve transaction details from the database.
        
        Args:
            transaction_id: ID of the transaction
            
        Returns:
            List of dictionaries containing transaction details
        """
        try:
            # Query the database
            self.db_manager.pos_db.execute(
                """
                SELECT s.product_id, p.name, s.quantity, p.price, s.total, s.discount, s.timestamp
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE s.transaction_id = ?
                """, 
                (transaction_id,)
            )
            
            results = self.db_manager.pos_db.fetchall()
            
            if not results:
                return []
            
            # Format results
            transaction_details = []
            for row in results:
                item = {
                    'product_id': row[0],
                    'name': row[1],
                    'quantity': row[2],
                    'price': row[3],
                    'total': row[4],
                    'discount': row[5],
                    'timestamp': row[6]
                }
                transaction_details.append(item)
            
            return transaction_details
        
        except Exception as e:
            print(f"Error getting transaction details: {str(e)}")
            return []
    
    def save_receipt(self, receipt_content, transaction_id):
        """Save receipt to a text file.
        
        Args:
            receipt_content: Formatted receipt content
            transaction_id: ID of the transaction
            
        Returns:
            Path to the saved receipt file or None if saving failed
        """
        try:
            # Create a filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{transaction_id}_{timestamp}.txt"
            filepath = os.path.join(self.receipt_dir, filename)
            
            # Write receipt to file
            with open(filepath, 'w') as f:
                f.write(receipt_content)
            
            return filepath
        
        except Exception as e:
            print(f"Error saving receipt: {str(e)}")
            return None
    
    def print_receipt(self, receipt_content):
        """Print the receipt to the default printer.
        
        Args:
            receipt_content: Formatted receipt content
            
        Returns:
            Boolean indicating success/failure
        """
        try:
            # Note: This is a simplified version that would need to be
            # replaced with actual printer interaction code for production use
            
            # For now, we'll just create a message saying it would print
            messagebox.showinfo("Print Receipt", 
                               "Receipt would be printed here in a real system.\n\n" +
                               "This function would connect to a receipt printer.")
            return True
            
            # In a real implementation, you might use a library like 'win32print'
            # or 'cups' depending on the operating system to handle printing
            
        except Exception as e:
            print(f"Error printing receipt: {str(e)}")
            return False
    
    def display_receipt(self, receipt_content, transaction_id):
        """Display receipt in a pop-up window with options to save or print.
        
        Args:
            receipt_content: Formatted receipt content
            transaction_id: ID of the transaction
        """
        receipt_window = tk.Toplevel()
        receipt_window.title(f"Receipt #{transaction_id}")
        receipt_window.attributes("-topmost", True)
        
        # Add a text widget to display the receipt
        text_widget = tk.Text(receipt_window, width=45, height=30, font=("Courier", 10))
        text_widget.insert(tk.END, receipt_content)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(padx=10, pady=10)
        
        # Add buttons for actions
        button_frame = tk.Frame(receipt_window)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(
            button_frame, 
            text="Save Receipt", 
            command=lambda: self._save_receipt_dialog(receipt_content, transaction_id, receipt_window)
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        print_btn = tk.Button(
            button_frame, 
            text="Print Receipt", 
            command=lambda: self.print_receipt(receipt_content)
        )
        print_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            button_frame, 
            text="Close", 
            command=receipt_window.destroy
        )
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def _save_receipt_dialog(self, receipt_content, transaction_id, parent_window):
        """Show dialog to save receipt to a specific location.
        
        Args:
            receipt_content: Formatted receipt content
            transaction_id: ID of the transaction
            parent_window: Parent window for the dialog
        """
        # Get default filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"receipt_{transaction_id}_{timestamp}.txt"
        
        # Show save dialog
        filepath = filedialog.asksaveasfilename(
            parent=parent_window,
            initialdir=os.getcwd(),
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(receipt_content)
                messagebox.showinfo("Success", f"Receipt saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save receipt: {str(e)}")