"""
Product Management Module
Handles product operations.
"""

from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager

class ProductManager:
    """Manages product operations."""
    
    def __init__(self):
        """Initialize the product manager."""
        self.db_manager = get_db_manager()
    
    def fetch_product_by_id(self, product_id: int) -> Optional[Tuple]:
        """Retrieve a product by its ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product tuple or None if not found
        """
        self.db_manager.pos_db.execute("SELECT * FROM products WHERE id=?", (product_id,))
        return self.db_manager.pos_db.fetchone()
    
    def fetch_product_by_barcode(self, product_barcode: str) -> Optional[Tuple]:
        """Retrieve a product by its barcode.
        
        Args:
            product_barcode: Product barcode
            
        Returns:
            Product tuple or None if not found
        """
        self.db_manager.pos_db.execute("SELECT * FROM products WHERE barcode=?", (product_barcode,))
        return self.db_manager.pos_db.fetchone()
    
    def fetch_products_by_category(self, category_id: int) -> List[Tuple]:
        """Retrieve all products in a specific category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of product tuples
        """
        self.db_manager.pos_db.execute("SELECT * FROM products WHERE category_id=?", (category_id,))
        return self.db_manager.pos_db.fetchall()
    
    def fetch_price_by_id(self, product_id: int) -> Optional[float]:
        """Retrieve the price of a product by its ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product price or None if not found
        """
        self.db_manager.pos_db.execute("SELECT price FROM products WHERE id=?", (product_id,))
        result = self.db_manager.pos_db.fetchone()
        return result[0] if result else None
    
    def fetch_all_products(self) -> List[Tuple]:
        """Retrieve all products from the database.
        
        Returns:
            List of product tuples
        """
        self.db_manager.pos_db.execute("SELECT * FROM products")
        return self.db_manager.pos_db.fetchall()
    
    def add_product(self, product_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a new product to the database.        
        Args:
            product_data: Dictionary containing product data with the following keys:
                - name: Product name
                - category_id: Category ID
                - price: Product price
                - stock: Initial stock quantity
                - barcode: Product barcode
                - description: Product description
                - supplier_id: Supplier ID
                - discount: Product discount percentage
                - unit_of_measurement: Unit of measurement
                - image_path: Path to product image
                - is_alcoholic: Boolean flag for alcoholic products
                - is_active: Boolean flag for active products
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Extract data from dictionary
            name = product_data.get('name')
            category_id = product_data.get('category_id')
            price = product_data.get('price')
            stock = product_data.get('stock')
            barcode = product_data.get('barcode')
            description = product_data.get('description')
            supplier_id = product_data.get('supplier_id')
            discount = product_data.get('discount', 0)
            unit_of_measurement = product_data.get('unit_of_measurement', 'unit')
            image_path = product_data.get('image_path')
            is_alcoholic = product_data.get('is_alcoholic', 0)
            is_active = product_data.get('is_active', 1)
            
            # Validate required fields
            required_fields = ['name', 'category_id', 'price', 'stock', 'barcode', 'supplier_id']
            missing_fields = [field for field in required_fields if product_data.get(field) is None]
            
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            
            # Insert the product
            self.db_manager.pos_db.execute('''
                INSERT INTO products (
                    name, category_id, price, stock, barcode, description, 
                    supplier_id, discount, unit_of_measurement, image_path, 
                    is_alcoholic, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, category_id, price, stock, barcode, description,
                supplier_id, discount, unit_of_measurement, image_path,
                is_alcoholic, is_active
            ))
            
            self.db_manager.commit_pos()
            return True, "Product added successfully"
        except Exception as e:
            if "UNIQUE constraint failed: products.barcode" in str(e):
                return False, "Barcode already exists"
            return False, f"Error adding product: {str(e)}"
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update an existing product in the database.
        
        Args:
            product_id: ID of the product to update
            product_data: Dictionary containing product data to update
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if product exists
            product = self.fetch_product_by_id(product_id)
            if not product:
                return False, "Product not found"
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = []
            
            # Map of field names to column names
            field_map = {
                'name': 'name',
                'category_id': 'category_id',
                'price': 'price',
                'stock': 'stock',
                'barcode': 'barcode',
                'description': 'description',
                'supplier_id': 'supplier_id',
                'discount': 'discount',
                'unit_of_measurement': 'unit_of_measurement',
                'image_path': 'image_path',
                'is_alcoholic': 'is_alcoholic',
                'is_active': 'is_active'
            }
            
            # Add fields to update query
            for field, column in field_map.items():
                if field in product_data and product_data[field] is not None:
                    update_fields.append(f"{column}=?")
                    params.append(product_data[field])
            
            # If no fields to update, return success
            if not update_fields:
                return True, "No changes to update"
                
            # Build and execute the update query
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id=?"
            params.append(product_id)
            
            self.db_manager.pos_db.execute(query, params)
            self.db_manager.commit_pos()
            
            return True, "Product updated successfully"
        except Exception as e:
            if "UNIQUE constraint failed: products.barcode" in str(e):
                return False, "Barcode already exists"
            return False, f"Error updating product: {str(e)}"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """Delete a product from the database.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if product exists
            product = self.fetch_product_by_id(product_id)
            if not product:
                return False, "Product not found"
            
            # Delete the product
            self.db_manager.pos_db.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.db_manager.commit_pos()
            
            return True, "Product removed successfully"
        except Exception as e:
            return False, f"Error removing product: {str(e)}"
    
    def update_stock(self, product_id: int, new_stock: int) -> Tuple[bool, str]:
        """Update the stock quantity of a product.
        
        Args:
            product_id: ID of the product
            new_stock: New stock quantity
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if product exists
            product = self.fetch_product_by_id(product_id)
            if not product:
                return False, "Product not found"
            
            # Update stock
            self.db_manager.pos_db.execute(
                "UPDATE products SET stock = ? WHERE id = ?", 
                (new_stock, product_id)
            )
            self.db_manager.commit_pos()
            
            return True, f"Stock updated to {new_stock}"
        except Exception as e:
            return False, f"Error updating stock: {str(e)}"
    
    def filter_products(self, filter_params: Dict[str, Any]) -> List[Tuple]:
        """Filter products based on search criteria.
        
        Args:
            filter_params: Dictionary containing filter parameters:
                - search_term: Text to search for
                - column: Column to search in
                - match_case: Whether to perform case-sensitive search
                - contains: Whether to search for contains or starts with
                
        Returns:
            List of filtered product tuples
        """
        search_term = filter_params.get('search_term', '')
        column = filter_params.get('column', 'name')
        match_case = filter_params.get('match_case', False)
        contains = filter_params.get('contains', True)
        
        # Map column names to indices in the product tuple
        column_mapping = {
            "ID": 0, "Product Name": 1, "Category": 2, "Price": 3, "Stock": 4, 
            "Barcode": 5, "Description": 6, "Supplier": 7, "Discount": 8, 
            "UoM": 9, "Date Added": 10, "Is Alcoholic": 11, "Is Active": 12,
        }
        
        column_index = column_mapping.get(column, 1)  # Default to name column
        
        # Get all products
        all_products = self.fetch_all_products()
        
        # Filter products
        filtered_products = []
        for product in all_products:
            value = str(product[column_index])
            
            if not match_case:
                value = value.lower()
                search_term = search_term.lower()
            
            if contains:
                if search_term in value:  # Contains search
                    filtered_products.append(product)
            else:
                if value.startswith(search_term):  # Starts with search
                    filtered_products.append(product)
        
        return filtered_products