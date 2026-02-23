"""
Base Window Module
Contains the base window class for UI components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Any, Callable, Tuple, Union, cast

import os

import config
from utils.alerts import get_alert_manager

class BaseWindow:
    """Base class for all windows in the application."""
    
    def __init__(self, root: Optional[tk.Tk] = None, title: Optional[str] = None, fullscreen: bool = False):
        """Initialize the base window.
        
        Args:
            root: The root Tkinter window or None to create a new one
            title: The window title
            fullscreen: Whether to display the window in fullscreen mode
        """
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Set window title
        if title:
            self.root.title(title)
        
        # Configure window
        self.root.configure(background=config.COLORS["background"])
        
        # Set fullscreen if requested
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        
        # Initialize alert manager
        self.alert_manager = get_alert_manager(self.root)
    
    def center_window(self, width: int = 800, height: int = 600) -> None:
        """Center the window on the screen.
        
        Args:
            width: Window width
            height: Window height
        """
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set window size and position
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_label(self, parent: tk.Widget, text: str, font_name: str = "default", 
                    row: Optional[int] = None, column: Optional[int] = None, **kwargs: Any) -> tk.Label:
        """Create a label with configured styles.
        
        Args:
            parent: Parent widget
            text: Label text
            font_name: Font name from config.FONTS
            row: Grid row (if using grid)
            column: Grid column (if using grid)
            **kwargs: Additional keyword arguments for the label
            
        Returns:
            The created label
        """
        # Create label with specified font
        font = config.FONTS.get(font_name, config.FONTS["default"])
        label = tk.Label(parent, text=text, font=font, **kwargs)
        
        # Place in grid if row and column are specified
        if row is not None and column is not None:
            grid_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['padx', 'pady', 'sticky', 'columnspan', 'rowspan']}
            label.grid(row=row, column=column, **grid_kwargs)
        
        return label
    
    def create_button(self, parent: tk.Widget, text: str, command: Callable[[], None], 
                     font_name: str = "button", bg_color: Optional[str] = None,
                     row: Optional[int] = None, column: Optional[int] = None, **kwargs: Any) -> tk.Button:
        """Create a button with configured styles.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command function
            font_name: Font name from config.FONTS
            bg_color: Background color
            row: Grid row (if using grid)
            column: Grid column (if using grid)
            **kwargs: Additional keyword arguments for the button
            
        Returns:
            The created button
        """
        # Create button with specified font and style
        font = config.FONTS.get(font_name, config.FONTS["button"])
        
        # Set up button arguments
        button_args: Dict[str, Any] = {
            'text': text,
            'font': font,
            'command': command,
            'relief': kwargs.pop('relief', tk.RAISED),
        }
        button_args.update(kwargs)
        
        # Add background color if specified
        if bg_color:
            button_args['bg'] = bg_color
        
        button = tk.Button(parent, **button_args)
        
        # Place in grid if row and column are specified
        if row is not None and column is not None:
            grid_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['padx', 'pady', 'sticky', 'columnspan', 'rowspan']}
            button.grid(row=row, column=column, **grid_kwargs)
        
        return button
    
    def create_entry(self, parent: tk.Widget, validate_command: Optional[Tuple[Any, ...]] = None,
                    font_name: str = "entry", row: Optional[int] = None, column: Optional[int] = None, 
                    **kwargs: Any) -> tk.Entry:
        """Create an entry with configured styles.
        
        Args:
            parent: Parent widget
            validate_command: Validation command tuple
            font_name: Font name from config.FONTS
            row: Grid row (if using grid)
            column: Grid column (if using grid)
            **kwargs: Additional keyword arguments for the entry
            
        Returns:
            The created entry
        """
        # Set up entry arguments
        font = config.FONTS.get(font_name, config.FONTS["entry"])
        entry_args: Dict[str, Any] = {'font': font}
        entry_args.update(kwargs)
        
        # Add validation if provided
        if validate_command:
            entry_args['validate'] = 'key'
            entry_args['validatecommand'] = validate_command
        
        entry = tk.Entry(parent, **entry_args)
        
        # Place in grid if row and column are specified
        if row is not None and column is not None:
            grid_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['padx', 'pady', 'sticky', 'columnspan', 'rowspan']}
            entry.grid(row=row, column=column, **grid_kwargs)
        
        return entry
    
    def create_combobox(self, parent: tk.Widget, values: List[str], state: str = "readonly",
                      font_name: str = "entry", row: Optional[int] = None, column: Optional[int] = None,
                      **kwargs: Any) -> ttk.Combobox:
        """Create a combobox with configured styles.
        
        Args:
            parent: Parent widget
            values: List of combobox values
            state: Combobox state ('readonly' or 'normal')
            font_name: Font name from config.FONTS
            row: Grid row (if using grid)
            column: Grid column (if using grid)
            **kwargs: Additional keyword arguments for the combobox
            
        Returns:
            The created combobox
        """
        # Create combobox
        combobox = ttk.Combobox(parent, values=values, state=state, **kwargs)
        
        # Configure style
        font = config.FONTS.get(font_name, config.FONTS["entry"])
        self.root.option_add("*TCombobox*Font", font)
        
        # Place in grid if row and column are specified
        if row is not None and column is not None:
            grid_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['padx', 'pady', 'sticky', 'columnspan', 'rowspan']}
            combobox.grid(row=row, column=column, **grid_kwargs)
        
        return combobox
    
    def create_treeview(self, parent: tk.Widget, columns: List[str], headings: Optional[List[str]] = None,
                       widths: Optional[List[int]] = None, anchors: Optional[List[str]] = None,
                       row: Optional[int] = None, column: Optional[int] = None, **kwargs: Any) -> ttk.Treeview:
        """Create a treeview with configured styles.
        
        Args:
            parent: Parent widget
            columns: Column IDs
            headings: Column headings (defaults to column IDs if None)
            widths: Column widths
            anchors: Column anchors ('w', 'e', 'center')
            row: Grid row (if using grid)
            column: Grid column (if using grid)
            **kwargs: Additional keyword arguments for the treeview
            
        Returns:
            The created treeview
        """
        # Create treeview
        tree = ttk.Treeview(parent, columns=columns, **kwargs)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#f0f0f0",
            foreground="#000000",
            rowheight=35,
            fieldbackground="#ffffff",
            font=("Segoe UI", 16)
        )
        
        style.configure(
            "Treeview.Heading", 
            font=("Segoe UI", 12, "bold"),
            padding=[10, 5, 10, 5]
        )
                
        style.map(
            "Treeview", 
            background=[("selected", "#4CAF50")],
            foreground=[("selected", "#FFFFFF")]
        )
        
        # Configure headings and columns
        for i, col_id in enumerate(columns):
            # Set heading
            heading_text = headings[i] if headings and i < len(headings) else col_id
            tree.heading(col_id, text=heading_text, anchor="w")
            
            # Set column width and anchor
            width = widths[i] if widths and i < len(widths) else 100
            anchor = anchors[i] if anchors and i < len(anchors) else "w"
            tree.column(col_id, width=width, anchor=anchor)
        
        # Configure tags for alternating row colors
        tree.tag_configure("evenrow", background="#f5f5f5")
        tree.tag_configure("oddrow", background="#ffffff")
        
        # Place in grid if row and column are specified
        if row is not None and column is not None:
            grid_kwargs = {k: v for k, v in kwargs.items() 
                          if k in ['padx', 'pady', 'sticky', 'columnspan', 'rowspan']}
            tree.grid(row=row, column=column, **grid_kwargs)
        
        return tree
    
    def disable_widgets(self, *widgets: tk.Widget) -> None:
        """Disable a list of widgets.
        
        Args:
            *widgets: Widgets to disable
        """
        for widget in widgets:
            if isinstance(widget, (tk.Button, tk.Entry, ttk.Button, ttk.Entry, ttk.Combobox)):
                widget.configure(state="disabled")
            elif isinstance(widget, tk.Frame):
                # Recursively disable all widgets in frame
                for child in widget.winfo_children():
                    self.disable_widgets(cast(tk.Widget, child))
    
    def enable_widgets(self, *widgets: tk.Widget) -> None:
        """Enable a list of widgets.
        
        Args:
            *widgets: Widgets to enable
        """
        for widget in widgets:
            if isinstance(widget, (tk.Button, tk.Entry, ttk.Button, ttk.Entry)):
                widget.configure(state="normal")
            elif isinstance(widget, ttk.Combobox):
                widget.configure(state="readonly")
            elif isinstance(widget, tk.Frame):
                # Recursively enable all widgets in frame
                for child in widget.winfo_children():
                    self.enable_widgets(cast(tk.Widget, child))
    
    def show_error(self, message: str) -> None:
        """Show an error message.
        
        Args:
            message: Error message
        """
        self.alert_manager.show_alert(message)
    
    def show_info(self, title: str, message: str) -> None:
        """Show an information message.
        
        Args:
            title: Message title
            message: Information message
        """
        self.alert_manager.show_info(title, message)
    
    def confirm(self, message: str, title: str) -> bool:
        """Show a confirmation dialog.
        
        Args:
            message: Confirmation message
            title: Dialog title
            
        Returns:
            True if confirmed, False otherwise
        """
        return self.alert_manager.show_yesno(message, title)
    
    def run(self) -> None:
        """Run the window's main loop."""
        self.root.mainloop()
    
    def close(self) -> None:
        """Close the window."""
        # Only destroy the root window if we own it
        if self.owns_root:
            self.root.destroy()