"""
Login Window Module
Handles user authentication and login.
"""

import os
import hashlib
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import config
from models.user import UserManager, RoleManager
from models.database import get_db_manager
from ui.base_window import BaseWindow

class LoginWindow(BaseWindow):
    """Login window for user authentication."""
    
    def __init__(self, root=None):
        """Initialize the login window.
        
        Args:
            root: The root Tkinter window or None to create a new one
        """
        super().__init__(root, "POS System Login", fullscreen=True)
        
        # Initialize models
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        
        # Initialize default roles when starting the application
        self.role_manager.initialize_default_roles()
        
        # Set up variables
        self.current_entry = None
        self.mode = "username"
        self.username = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Create main frame for login
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
        
        # Calculate frame size (approximately 2/3 of screen width for touchscreen)
        frame_width = int(screen_width / 1.5)
        frame_height = int(screen_height / 1.5)
        
        # Position frame in center
        x_position = (screen_width - frame_width) // 2
        y_position = (screen_height - frame_height) // 2
        
        self.main_frame.place(
            x=x_position, 
            y=y_position, 
            width=frame_width, 
            height=frame_height
        )
        
        # Add logo or title
        self.setup_title()
        
        # Add login form
        self.setup_login_form()
        
        # Add keypad
        self.create_keypad()
        
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
        
        # Bind Enter key
        self.root.bind("<Return>", lambda event: self.on_keypad_button("Enter"))
    
    def setup_title(self):
        """Set up the header section with logo/title."""
        header_frame = tk.Frame(self.main_frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(40, 30))

        """Create a text title for the login screen."""
        title_label = tk.Label(
            header_frame,
            text="Point of Sale System",
            font=config.FONTS["large_button"],
            bg="white",
            fg="black"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Login to continue",
            font=config.FONTS["header"],
            bg="white",
            fg="black"
        )
        subtitle_label.pack()
    
    def setup_login_form(self):
        """Set up the username and password entry form."""
        form_frame = tk.Frame(self.main_frame, bg="white")
        form_frame.pack(fill="x", padx=60, pady=20)
        
        # Username label and entry
        self.entry_label = tk.Label(
            form_frame, 
            text="Username:",
            font=config.FONTS["header"],
            bg="white",
            fg="black"
        )
        self.entry_label.pack(anchor="w", pady=(0, 5))
        
        self.entry = tk.Entry(
            form_frame,
            font=config.FONTS["entry"],
            width=25,
            bd=2,
            relief="solid"
        )
        self.entry.pack(fill="x", pady=(0, 20), ipady=10)
        self.entry.focus()
        
        # Remember the current entry for keypad input
        self.current_entry = self.entry
        
        # Bind the entry to the focus event
        self.entry.bind("<FocusIn>", self.set_current_entry)
    
    def create_keypad(self):
        """Create the numeric keypad for input."""
        keypad_frame = tk.Frame(self.main_frame, bg="white")
        keypad_frame.pack(padx=60, pady=(20, 40), fill="both", expand=True)
        
        # Configure grid to fill available space
        for i in range(4):
            keypad_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        for i in range(4):
            keypad_frame.grid_rowconfigure(i, weight=1, uniform="equal")
        
        # Button layout
        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2), 
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("0", 3, 1)
        ]
        
        # Create number buttons with bigger size and padding
        for text, row, col in buttons:
            button = tk.Button(
                keypad_frame,
                text=text,
                font=config.FONTS["keypad_button"],
                bg=config.COLORS["control_buttons"],
                fg="white",
                command=lambda t=text: self.on_keypad_button(t),
                relief="flat"
            )
            button.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipadx=20, ipady=20)
            
            # Add hover effect
            button.bind("<Enter>", lambda e, b=button: b.config(bg="#1c9fe0"))
            button.bind("<Leave>", lambda e, b=button: b.config(bg=config.COLORS["control_buttons"]))
        
        # Special function buttons with different colors
        clear_button = tk.Button(
            keypad_frame,
            text="Clear",
            font=config.FONTS["keypad_button"],
            bg="#FFA500",  # Orange
            fg="white",
            command=lambda: self.on_keypad_button("Clear"),
            relief="flat"
        )
        clear_button.grid(row=3, column=0, padx=8, pady=8, sticky="nsew", ipadx=20, ipady=20)
        
        backspace_button = tk.Button(
            keypad_frame,
            text="⌫",
            font=config.FONTS["keypad_button"],
            bg="#FFA500",  # Orange
            fg="white",
            command=lambda: self.on_keypad_button("⌫"),
            relief="flat"
        )
        backspace_button.grid(row=3, column=2, padx=8, pady=8, sticky="nsew", ipadx=20, ipady=20)
        
        # Column for special buttons
        keypad_frame.grid_columnconfigure(3, weight=1, uniform="equal")
        
        # Special buttons on the right side
        enter_button = tk.Button(
            keypad_frame,
            text="Enter",
            font=config.FONTS["keypad_button"],
            bg=config.COLORS["transaction_frame"],
            fg="white",
            command=lambda: self.on_keypad_button("Enter"),
            relief="flat"
        )
        enter_button.grid(row=0, column=3, rowspan=4, padx=8, pady=8, sticky="nsew", ipadx=25, ipady=40)

    def set_current_entry(self, event):
        """Set the current entry field for input."""
        self.current_entry = event.widget
    
    def on_keypad_button(self, char):
        """Handle keypad button clicks."""
        if not self.current_entry:
            return
            
        current_text = self.current_entry.get()
        
        if char == "⌫":
            # Backspace - delete last character
            self.current_entry.delete(len(current_text) - 1, tk.END)
        elif char == "Clear":
            # Clear - delete all text
            self.current_entry.delete(0, tk.END)
        elif char == "Enter":
            # Enter - process the current entry
            self.process_entry()
        else:
            # Add the character to the entry
            self.current_entry.insert(tk.END, char)
    
    def process_entry(self):
        """Process the current entry based on mode."""
        if not self.current_entry:
            return
            
        input_value = self.current_entry.get()
        
        if not input_value:
            self.show_error("Please enter a value.")
            return
            
        if self.mode == "username":
            self.check_username(input_value)
        elif self.mode == "password":
            self.login(input_value)
    
    def check_username(self, username):
        """Check if the username exists."""
        # Query the database for the username
        db_manager = get_db_manager()
        db_manager.users_db.execute("SELECT username FROM users WHERE username=?", (username,))
        user = db_manager.users_db.fetchone()
        
        if user:
            self.set_password_mode()
            self.username = username
        else:
            self.show_error("Username not recognized. Please try again.")
            self.current_entry.delete(0, tk.END)
    
    def set_password_mode(self):
        """Switch to password entry mode."""
        self.mode = "password"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
            self.current_entry.config(show="*")
        self.entry_label.config(text="Password:")
    
    def set_username_mode(self):
        """Switch to username entry mode."""
        self.mode = "username"
        if self.current_entry:
            self.current_entry.delete(0, tk.END)
            self.current_entry.config(show="")
        self.entry_label.config(text="Username:")
    
    def login(self, password):
        """Verify login credentials and start the main application."""
        # Check login credentials
        is_valid, user_id = self.user_manager.verify_login(self.username, password)
        
        if is_valid:
            # Save the username for the POS window
            username = self.username
            
            # Reset the alert manager singleton so it gets recreated with the new root
            import utils.alerts
            utils.alerts._alert_manager = None
            
            # Destroy the login window completely
            self.root.destroy()
            
            # Start the main application with a new root
            from ui.pos_window import POSWindow
            new_root = tk.Tk()
            app = POSWindow(new_root, username)
            app.run()
        else:
            self.current_entry.delete(0, tk.END)
            self.set_username_mode()
            self.show_error("Invalid username or password")