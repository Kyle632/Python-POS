"""
Alert System Module
Handles popup alerts and dialog boxes.
"""

import tkinter as tk
from tkinter import font as tk_font
from typing import Callable, Optional

class AlertManager:
    """Handles popup alerts and dialog boxes."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the alert manager.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        
        # Store active alerts
        self.alerts: list = []
        self.infos: list = []
        self.yesnos: list = []
        
        # Configure fonts and colors
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure fonts and colors for alerts."""
        self.title_font = tk_font.Font(font=("Segoe UI Semibold", 22), weight="bold")
        self.message_font = tk_font.Font(font=("Segoe UI Semilight", 20))
        self.button_font = tk_font.Font(font=("Segoe UI", 18))
        
        self.green_bg = "#73bf65"
        self.red_bg = "#f56342"
    
    def show_alert(self, message: str) -> None:
        """Show an error alert dialog.
        
        Args:
            message: The error message to display
        """
        alert_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        alert_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.alerts.append(alert_frame)
        
        title_label = tk.Label(alert_frame, text="Error", font=self.title_font, bg="white")
        title_label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="W")
        
        msg_label = tk.Label(alert_frame, text=message, font=self.message_font, wraplength=350, bg="white")
        msg_label.grid(row=1, column=0, pady=5, padx=10)
        
        ok_button = tk.Button(
            alert_frame, 
            text="OK", 
            font=self.button_font, 
            command=lambda: self._close_alert(alert_frame), 
            width=10, 
            height=1, 
            bg=self.red_bg
        )
        ok_button.grid(row=2, column=0, pady=(5, 10), padx=10, sticky="ESW")
        
        self.root.attributes("-topmost", True)
        self.root.update()
        self.root.attributes("-topmost", False)
    
    def show_info(self, title: str, message: str) -> None:
        """Show an information dialog.
        
        Args:
            title: The dialog title
            message: The information message to display
        """
        info_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        info_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.infos.append(info_frame)
        
        title_label = tk.Label(info_frame, text=f"Info: {title}", font=self.title_font, bg="white")
        title_label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="W")
        
        msg_label = tk.Label(info_frame, text=message, font=self.message_font, wraplength=350, bg="white")
        msg_label.grid(row=1, column=0, pady=5, padx=10)
        
        ok_button = tk.Button(
            info_frame, 
            text="OK", 
            font=self.button_font, 
            command=lambda: self._close_info(info_frame), 
            width=10, 
            height=1, 
            bg=self.green_bg
        )
        ok_button.grid(row=2, column=0, pady=(5, 10), padx=10, sticky="ESW")
        
        self.root.attributes("-topmost", True)
        self.root.update()
        self.root.attributes("-topmost", False)
    
    def show_yesno(self, message: str, title: str) -> bool:
        """Show a Yes/No confirmation dialog.
        
        Args:
            message: The question message
            title: The dialog title
            
        Returns:
            True if Yes was clicked, False if No was clicked
        """
        result_var = tk.BooleanVar()
        
        yesno_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        yesno_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.yesnos.append(yesno_frame)
        
        title_label = tk.Label(yesno_frame, text=title, font=self.title_font, bg="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="W")
        
        msg_label = tk.Label(yesno_frame, text=message, font=self.message_font, wraplength=350, bg="white")
        msg_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="EW")
        
        yes_button = tk.Button(
            yesno_frame, 
            text="Yes", 
            font=self.button_font, 
            command=lambda: self._set_result(True, result_var, yesno_frame), 
            width=10, 
            height=1, 
            bg=self.green_bg
        )
        yes_button.grid(row=2, column=0, pady=(5, 10), padx=10, sticky="EW")
        
        no_button = tk.Button(
            yesno_frame, 
            text="No", 
            font=self.button_font, 
            command=lambda: self._set_result(False, result_var, yesno_frame), 
            width=10, 
            height=1, 
            bg=self.red_bg
        )
        no_button.grid(row=2, column=1, pady=(5, 10), padx=10, sticky="EW")
        
        yesno_frame.grid_columnconfigure(0, weight=1)
        yesno_frame.grid_columnconfigure(1, weight=1)
        
        self.root.attributes("-topmost", True)
        self.root.update()
        self.root.attributes("-topmost", False)
        
        self.root.wait_variable(result_var)
        return result_var.get()
    
    def _set_result(self, value: bool, result_var: tk.BooleanVar, yesno_frame: tk.Frame) -> None:
        """Set the result of a Yes/No dialog and close it.
        
        Args:
            value: The result value (True for Yes, False for No)
            result_var: The BooleanVar to store the result
            yesno_frame: The frame to close
        """
        result_var.set(value)
        self._close_yesno(yesno_frame)
    
    def _close_alert(self, alert_frame: tk.Frame) -> None:
        """Close an alert dialog.
        
        Args:
            alert_frame: The frame to close
        """
        if alert_frame in self.alerts:
            alert_frame.destroy()
            self.alerts.remove(alert_frame)
    
    def _close_info(self, info_frame: tk.Frame) -> None:
        """Close an information dialog.
        
        Args:
            info_frame: The frame to close
        """
        if info_frame in self.infos:
            info_frame.destroy()
            self.infos.remove(info_frame)
    
    def _close_yesno(self, yesno_frame: tk.Frame) -> None:
        """Close a Yes/No dialog.
        
        Args:
            yesno_frame: The frame to close
        """
        if yesno_frame in self.yesnos:
            yesno_frame.destroy()
            self.yesnos.remove(yesno_frame)


# Global instance
_alert_manager = None

def get_alert_manager(root: Optional[tk.Tk] = None) -> AlertManager:
    """Get the singleton instance of AlertManager.
    
    Args:
        root: The root Tkinter window (required on first call)
        
    Returns:
        The AlertManager instance
        
    Raises:
        ValueError: If root is not provided on first call
    """
    global _alert_manager
    if _alert_manager is None:
        if root is None:
            raise ValueError("Root window must be provided on first call")
        _alert_manager = AlertManager(root)
    elif root is not None and _alert_manager.root != root:
        # If a different root is provided, update the alert manager to use the new root
        _alert_manager = AlertManager(root)
    return _alert_manager