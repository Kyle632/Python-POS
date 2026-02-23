"""
Setup Window Module
Handles first-time system setup and initial user creation.
"""

import tkinter as tk
from tkinter import ttk
import hashlib

import config
from models.user import UserManager, RoleManager
from models.database import get_db_manager
from ui.base_window import BaseWindow
from ui.login_window import LoginWindow

class SetupWindow(BaseWindow):
    """Setup window for first-time system configuration."""
    
    def __init__(self, root=None):
        """Initialize the setup window.
        
        Args:
            root: The root Tkinter window or None to create a new one
        """
        super().__init__(root, "POS System Setup", fullscreen=True)
        
        # Initialize models
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        
        # Initialize default roles
        self.role_manager.initialize_default_roles()
        
        # Set up variables
        self.current_entry = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Create main frame for setup
        self.main_frame = tk.Frame(
            self.root, 
            bg="white",
            highlightbackground=config.COLORS["transaction_frame"],
            highlightthickness=2,
            bd=0
        )
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate frame size
        self.frame_width = int(screen_width / 1.5)
        self.frame_height = int(screen_height / 1.5)
        
        # Position frame in center
        x_position = (screen_width - self.frame_width) // 2
        y_position = (screen_height - self.frame_height) // 2
        
        self.main_frame.place(
            x=x_position, 
            y=y_position, 
            width=self.frame_width, 
            height=self.frame_height
        )
        
        # Add title
        self.setup_title()
        
        # Create the scrollable area
        canvas = tk.Canvas(self.main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        
        # Configure the scrolling region
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a window in the canvas to hold the scrollable frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Setup form in the scrollable frame
        self.setup_form(scrollable_frame)
        
        # Add exit button
        exit_button = tk.Button(
            self.root,
            text="Exit",
            font=config.FONTS["header"],
            bg="#f44336",
            fg="white",
            command=self.root.destroy,
            padx=25,
            pady=15,
            relief="flat"
        )
        exit_button.place(x=30, y=30)
    
    def setup_title(self):
        """Set up the header section with title and welcome message."""
        header_frame = tk.Frame(self.main_frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(40, 20))

        title_label = tk.Label(
            header_frame,
            text="Welcome to Point of Sale System",
            font=("Segoe UI", 34, "bold"),
            bg="white",
            fg="black"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="First-Time Setup",
            font=("Segoe UI", 24),
            bg="white",
            fg="black"
        )
        subtitle_label.pack()
        
        welcome_text = (
            "Thank you for choosing our Point of Sale System. "
            "Since this is your first time running the application, "
            "we need to create an administrator account."
        )
        
        welcome_label = tk.Label(
            header_frame,
            text=welcome_text,
            font=("Segoe UI", 16),
            bg="white",
            fg="black",
            wraplength=self.frame_width - 100,
            justify="center"
        )
        welcome_label.pack(pady=20)
    
    def setup_form(self, parent_frame):
        """Set up the user creation form."""
        form_frame = tk.Frame(parent_frame, bg="white")
        form_frame.pack(fill="x", padx=40, pady=10)
        
        # Admin information
        tk.Label(
            form_frame, 
            text="Create Administrator Account",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="black"
        ).pack(anchor="w", pady=(10, 20))
        
        # Username
        tk.Label(
            form_frame, 
            text="Username:",
            font=config.FONTS["entry"],
            bg="white",
            fg="black"
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=config.FONTS["entry"],
            width=25,
            bd=2,
            relief="solid"
        )
        self.username_entry.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Password
        tk.Label(
            form_frame, 
            text="Password:",
            font=config.FONTS["entry"],
            bg="white",
            fg="black"
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=config.FONTS["entry"],
            width=25,
            bd=2,
            relief="solid",
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Confirm Password
        tk.Label(
            form_frame, 
            text="Confirm Password:",
            font=config.FONTS["entry"],
            bg="white",
            fg="black"
        ).pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(
            form_frame,
            font=config.FONTS["entry"],
            width=25,
            bd=2,
            relief="solid",
            show="*"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Store name (optional)
        tk.Label(
            form_frame, 
            text="Store Name (Optional):",
            font=config.FONTS["entry"],
            bg="white",
            fg="black"
        ).pack(anchor="w", pady=(0, 5))
        
        self.store_name_entry = tk.Entry(
            form_frame,
            font=config.FONTS["entry"],
            width=25,
            bd=2,
            relief="solid"
        )
        self.store_name_entry.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Status message
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=config.FONTS["default"],
            bg="white",
            fg="red"
        )
        self.status_label.pack(anchor="w", pady=(0, 20))
        
        # Create user button
        create_button = tk.Button(
            form_frame,
            text="Create Admin Account",
            font=config.FONTS["button"],
            bg=config.COLORS["transaction_frame"],
            fg="white",
            command=self.create_admin_user,
            relief="flat",
            padx=20,
            pady=10
        )
        create_button.pack(pady=20)
    
    def create_admin_user(self):
        """Create the administrator user account."""
        # Get form values
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        store_name = self.store_name_entry.get().strip()
        
        # Validate inputs
        if not username:
            self.status_label.config(text="Username is required")
            return
        
        if len(username) < 3:
            self.status_label.config(text="Username must be at least 3 characters")
            return
        
        if not password:
            self.status_label.config(text="Password is required")
            return
        
        if len(password) < 6:
            self.status_label.config(text="Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            self.status_label.config(text="Passwords do not match")
            return
        
        # Get administrator role ID
        admin_role_id = None
        roles = self.role_manager.get_all_roles()
        for role in roles:
            if role[1].lower() == "administrator":
                admin_role_id = role[0]
                break
        
        if not admin_role_id:
            # Create administrator role if it doesn't exist
            success, message = self.role_manager.add_role("Administrator")
            if success:
                roles = self.role_manager.get_all_roles()
                for role in roles:
                    if role[1].lower() == "administrator":
                        admin_role_id = role[0]
                        break
            else:
                self.status_label.config(text=f"Error creating administrator role: {message}")
                return
        
        # Create the administrator user
        success, message = self.user_manager.add_user(username, password, admin_role_id)
        
        if success:
            # Save store name if provided
            if store_name:
                # Update the app name in the config
                config.APP_NAME = store_name
                
                # Here you might want to save this to a settings file
                # For now, we'll just update the in-memory config
                
            # Show success message
            self.show_info("Setup Complete", "Administrator account created successfully.\n\nYou can now log in.")
            
            # Close setup window and open login window
            self.close_and_open_login()
        else:
            self.status_label.config(text=f"Error creating user: {message}")
    
    def close_and_open_login(self):
        """Close the setup window and open the login window."""
        # Reset the alert manager singleton
        import utils.alerts
        utils.alerts._alert_manager = None
        
        # Destroy the setup window
        self.root.destroy()
        
        # Start the login window with a new root
        new_root = tk.Tk()
        login_window = LoginWindow(new_root)
        login_window.run()