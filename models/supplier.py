"""
Supplier Management Module
Handles supplier operations.
"""

from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager

class SupplierManager:
    """Manages supplier operations."""
    
    def __init__(self):
        """Initialize the supplier manager."""
        self.db_manager = get_db_manager()
    
    def fetch_all_suppliers(self) -> List[Tuple]:
        """Retrieve all suppliers from the database.
        
        Returns:
            List of supplier tuples
        """
        self.db_manager.pos_db.execute("SELECT * FROM suppliers")
        return self.db_manager.pos_db.fetchall()
    
    def fetch_supplier_by_name(self, supplier_name: str) -> Optional[int]:
        """Retrieve a supplier ID by name.
        
        Args:
            supplier_name: Supplier name
            
        Returns:
            Supplier ID or None if not found
        """
        self.db_manager.pos_db.execute("SELECT id FROM suppliers WHERE name=?", (supplier_name,))
        result = self.db_manager.pos_db.fetchone()
        return result[0] if result else None
    
    def fetch_supplier_by_id(self, supplier_id: int) -> Optional[str]:
        """Retrieve a supplier name by ID.
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Supplier name or None if not found
        """
        self.db_manager.pos_db.execute("SELECT name FROM suppliers WHERE id=?", (supplier_id,))
        result = self.db_manager.pos_db.fetchone()
        return result[0] if result else None
    
    def add_supplier(self, name: str, contact_info: str) -> Tuple[bool, str]:
        """Add a new supplier to the database.
        
        Args:
            name: The supplier name
            contact_info: Contact information for the supplier
            
        Returns:
            Tuple containing success status and message
        """
        try:
            self.db_manager.pos_db.execute(
                "INSERT INTO suppliers (name, contact_info) VALUES (?, ?)",
                (name, contact_info)
            )
            self.db_manager.commit_pos()
            return True, f"Supplier '{name}' added successfully"
        except Exception as e:
            if "UNIQUE constraint failed: suppliers.name" in str(e):
                return False, f"Supplier '{name}' already exists"
            return False, f"Error adding supplier: {str(e)}"
    
    def update_supplier(self, supplier_id: int, name: str, contact_info: str) -> Tuple[bool, str]:
        """Update an existing supplier.
        
        Args:
            supplier_id: The ID of the supplier to update
            name: The new supplier name
            contact_info: New contact information
            
        Returns:
            Tuple containing success status and message
        """
        try:
            self.db_manager.pos_db.execute(
                "UPDATE suppliers SET name=?, contact_info=? WHERE id=?",
                (name, contact_info, supplier_id)
            )
            self.db_manager.commit_pos()
            return True, f"Supplier updated successfully"
        except Exception as e:
            if "UNIQUE constraint failed: suppliers.name" in str(e):
                return False, f"Supplier name '{name}' already exists"
            return False, f"Error updating supplier: {str(e)}"
    
    def delete_supplier(self, supplier_id: int) -> Tuple[bool, str]:
        """Delete a supplier from the database.
        
        Args:
            supplier_id: The ID of the supplier to delete
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if supplier is associated with any products
            self.db_manager.pos_db.execute(
                "SELECT COUNT(*) FROM products WHERE supplier_id=?", 
                (supplier_id,)
            )
            count = self.db_manager.pos_db.fetchone()[0]
            
            if count > 0:
                return False, f"Cannot delete supplier: {count} products are associated with this supplier"
            
            # Delete the supplier
            self.db_manager.pos_db.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
            self.db_manager.commit_pos()
            return True, "Supplier deleted successfully"
        except Exception as e:
            return False, f"Error deleting supplier: {str(e)}"