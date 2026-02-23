"""
Category Management Module
Handles product category operations.
"""

from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager

class CategoryManager:
    """Manages product category operations."""
    
    def __init__(self):
        """Initialize the category manager."""
        self.db_manager = get_db_manager()
    
    def fetch_all_categories(self) -> List[Tuple]:
        """Retrieve all categories from the database.
        
        Returns:
            List of category tuples
        """
        self.db_manager.pos_db.execute("SELECT * FROM categories")
        return self.db_manager.pos_db.fetchall()
    
    def fetch_category_by_id(self, category_id: int) -> Optional[Tuple]:
        """Retrieve a category by its ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category tuple or None if not found
        """
        self.db_manager.pos_db.execute("SELECT * FROM categories WHERE id=?", (category_id,))
        return self.db_manager.pos_db.fetchone()
    
    def fetch_category_by_name(self, category_name: str) -> Optional[int]:
        """Retrieve a category ID by name.
        
        Args:
            category_name: Category name
            
        Returns:
            Category ID or None if not found
        """
        self.db_manager.pos_db.execute("SELECT id FROM categories WHERE name=?", (category_name,))
        result = self.db_manager.pos_db.fetchone()
        return result[0] if result else None
    
    def add_category(self, name: str, discount: int, image_path: Optional[str] = None) -> Tuple[bool, str]:
        """Add a new category to the database.
        
        Args:
            name: Category name
            discount: Category discount percentage
            image_path: Optional path to category image
            
        Returns:
            Tuple containing success status and message
        """
        try:
            self.db_manager.pos_db.execute(
                "INSERT INTO categories (name, discount, image_path) VALUES (?, ?, ?)", 
                (name, discount, image_path)
            )
            self.db_manager.commit_pos()
            return True, f"Category '{name}' added successfully"
        except Exception as e:
            if "UNIQUE constraint failed: categories.name" in str(e):
                return False, "Category already exists"
            return False, f"Error adding category: {str(e)}"
    
    def update_category(self, category_id: int, new_name: str, new_discount: int, 
                        new_image_path: Optional[str] = None) -> Tuple[bool, str]:
        """Update a category's properties.
        
        Args:
            category_id: ID of the category to update
            new_name: New category name
            new_discount: New discount percentage
            new_image_path: Optional path to new category image
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Update name and discount
            self.db_manager.pos_db.execute(
                "UPDATE categories SET name=?, discount=? WHERE id=?", 
                (new_name, new_discount, category_id)
            )
            
            # Update image path if provided
            if new_image_path:
                self.db_manager.pos_db.execute(
                    "UPDATE categories SET image_path=? WHERE id=?", 
                    (new_image_path, category_id)
                )
                
            self.db_manager.commit_pos()
            return True, f"Category '{new_name}' updated successfully"
        except Exception as e:
            if "UNIQUE constraint failed: categories.name" in str(e):
                return False, "Category already exists"
            return False, f"Error updating category: {str(e)}"
    
    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """Delete a category from the database.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if category is associated with any products
            self.db_manager.pos_db.execute(
                "SELECT COUNT(*) FROM products WHERE category_id=?", 
                (category_id,)
            )
            count = self.db_manager.pos_db.fetchone()[0]
            
            if count > 0:
                return False, f"Cannot delete category: {count} products are assigned to this category"
            
            # Delete the category
            self.db_manager.pos_db.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.db_manager.commit_pos()
            return True, "Category deleted successfully"
        except Exception as e:
            return False, f"Error deleting category: {str(e)}"