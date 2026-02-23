"""
Configuration settings for the Point of Sale System.
Contains constants, styles, and system-wide settings.
"""

import os

# Application info
APP_NAME = "Point of Sale System"
VERSION = "1.0.0"

# Database settings
DB_POS_PATH = 'pos.db'
DB_USERS_PATH = 'users.db'

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
PRODUCT_IMAGES_DIR = os.path.join(ASSETS_DIR, 'product_images')

# Ensure directories existx
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(PRODUCT_IMAGES_DIR, exist_ok=True)

# Default image for products without images
DEFAULT_IMAGE_PATH = os.path.join(ASSETS_DIR, 'no_image.jpg')

MIN_SCREEN_WIDTH = 1280
MIN_SCREEN_HEIGHT = 1024

# UI Colors
COLORS = {
    "background": "#F0F0F0",
    "top_bar": "#000000",
    "transaction_frame": "#FF7062",
    "control_buttons": "#26b3f0",
    "keypad": "#77DD77",    
    "category_frame": "#ff964f",
    "pay_frame": "#f04b26",
}

# UI Fonts
FONTS = {
    "default": ("Segoe UI Semilight", 12),
    "header": ("Segoe UI Semibold", 20),
    "button": ("Segoe UI Semibold", 16),
    "large_button": ("Segoe UI Semibold", 32),
    "keypad_button": ("Segoe UI Semibold", 30),
    "pay_label": ("Segoe UI Semibold", 30),
    "entry": ("Segoe UI Semibold", 15),
}

# Default roles
DEFAULT_ROLES = [
    "Administrator",
    "Manager",
    "Cashier",
    "Stock Clerk"
]

