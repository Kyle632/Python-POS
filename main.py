"""
Point of Sale System - Main Entry Point
This is the main entry point for the POS application.
"""

import os
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configurations
try:
    import config
except ImportError:
    tk.messagebox.showerror(
        "Import Error",
        "Could not import configuration. Please ensure config.py exists."
    )
    sys.exit(1)

def check_screen_size():
    """Check if screen meets minimum size requirements and warn if not met."""
    temp_root = tk.Tk() #Temp
    
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
   
    if screen_width < config.MIN_SCREEN_WIDTH or screen_height < config.MIN_SCREEN_HEIGHT:
        temp_root.withdraw()  # Hide the temporary window
        proceed = messagebox.askyesno(
            "Screen Size Warning",
            f"This application is designed for a minimum screen resolution of {config.MIN_SCREEN_WIDTH}x{config.MIN_SCREEN_HEIGHT}.\n"
            f"Your current resolution is {screen_width}x{screen_height}.\n\n"
            f"Some interface elements may not display correctly or be inaccessible.\n"
            f"Do you wish to proceed anyway?"
        )
        temp_root.destroy()
        return proceed
    
    # Clean up the temporary window
    temp_root.destroy()
    return True

def is_first_run():
    """Check if this is the first run of the application by checking if any users exist."""
    try:
        from models.user import UserManager
        
        # Check if any users exist
        user_manager = UserManager()
        return not user_manager.has_users()
    except Exception as e:
        print(f"Error checking if first run: {str(e)}")
        return False
    
    
def start_setup_screen():
    """Start the application by launching the setup screen."""
    try:
        from ui.setup_window import SetupWindow
        root = tk.Tk()
        setup_window = SetupWindow(root)
        setup_window.run()
    except Exception as e:
        show_error(e)

def start_login_screen():
    """Start the application by launching the login screen."""
    try:

        if not check_screen_size():
            print("Application terminated due to insufficient screen resolution.")
            sys.exit(0)  # Exit cleanly, not an error#

        if is_first_run():
            print("First run detected. Starting setup screen.")
            start_setup_screen()
            return

        from ui.login_window import LoginWindow
        root = tk.Tk()
        login_window = LoginWindow(root)
        login_window.run()
    except Exception as e:
        show_error(e)

def show_error(exception):
    """Display error message for critical failures."""
    error_message = f"An error occurred: {str(exception)}\n\n{traceback.format_exc()}"
    print(error_message)  # Log to console
    
    # Try to show a graphical error dialog
    try:
        tk.messagebox.showerror("Error", error_message)
    except:
        # If that fails, just print to console
        print("Could not display graphical error message.")
    
    sys.exit(1)

if __name__ == "__main__":
    # Set up error handling

    try:
        # Initialize system directories
        os.makedirs(config.ASSETS_DIR, exist_ok=True)
        os.makedirs(config.PRODUCT_IMAGES_DIR, exist_ok=True)
        
        # Start the application
        start_login_screen()
    except Exception as e:
        show_error(e)
4