"""
String Constants
Contains error and information messages used throughout the application.
"""

# Error messages
ERROR_STRINGS = {
    "no_product": "Product not found.",
    "all_fields": "All fields are required to be filled in.",
    "select_product": "Please select a product.",
    "username_exists": "Username already exists.",
    "invalid_quantity": "Invalid quantity provided.",
    "invalid_discount": "Invalid discount provided. Must be between 0 and 100.",
    "category_exists": "Category already exists.",
    "error_removing_product": "Error removing product: ",
    "error_adding_product": "Error adding product: ",
    "error_updating_product": "Error updating product: "
}

# Information messages
INFO_STRINGS = {
    "user_added": "User successfully added.",
    "user_removed": "User successfully removed.",
    "product_added": "Product added successfully.",
    "product_updated": "Product updated successfully.",
    "product_removed": "Product removed successfully.",
    "product_removal_cancelled": "Product removal cancelled.",
    "alcohol_check": "Item scanned is classed as alcohol. Please check the customer is over 18.",
    "no_stock": "Not enough stock."
}