"""
Image Handler Module
Provides utilities for handling product images in the POS system.
"""

import os
import sys
import traceback
from typing import Optional, Tuple, Dict
from PIL import Image, ImageTk
import datetime

import config

class ImageHandler:
    """Handles loading, saving, and caching product images."""
    
    def __init__(self):
        """Initialize the image handler with cache and default paths."""
        self._image_cache: Dict[str, ImageTk.PhotoImage] = {}
        self.default_image_path = config.DEFAULT_IMAGE_PATH
        
        self.setup_image_directory()
        
        # Load the default image as a PIL Image, not a PhotoImage
        self._default_pil_image = None
        self._default_photo = None
        self._load_default_image((200, 200))
    
    def setup_image_directory(self) -> None:
        """Create the product images directory if it doesn't exist."""
        if not os.path.exists(config.PRODUCT_IMAGES_DIR):
            try:
                os.makedirs(config.PRODUCT_IMAGES_DIR, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
    
    def _load_default_image(self, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
        """Load the default image at the specified size."""
        try:
            if not os.path.exists(self.default_image_path):
                # Try to find it elsewhere
                alternative_paths = [
                    os.path.join(config.ASSETS_DIR, "no_image.jpg"),
                    os.path.join(config.BASE_DIR, "assets", "no_image.jpg"),
                    os.path.join(os.path.dirname(config.BASE_DIR), "assets", "no_image.jpg")
                ]
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        self.default_image_path = alt_path
                        break
                
                if not os.path.exists(self.default_image_path):
                    # Create a blank image as a last resort
                    img = Image.new('RGB', size, color='gray')
                    self._default_pil_image = img
                    return None
            
            with Image.open(self.default_image_path) as img:
                img = img.convert('RGB')
                img = img.resize(size, Image.Resampling.LANCZOS)
                self._default_pil_image = img.copy()
                return None
        except Exception as e:
            print(f"Error loading default image: {e}")
            img = Image.new('RGB', size, color='gray')
            self._default_pil_image = img
            return None
    
    def fix_path(self, path: Optional[str]) -> Optional[str]:
        """
        Fix common path issues, like incorrect directory names.
        
        Args:
            path: Path to fix
            
        Returns:
            Fixed path or None
        """
        if not path:
            return None
            
        # Fix the POS vs POSNEW directory mismatch
        if "\\Desktop\\POS\\" in path:
            fixed_path = path.replace("\\Desktop\\POS\\", "\\Desktop\\POSNEW\\")
            return fixed_path
        
        return path
    
    def get_absolute_path(self, relative_path: Optional[str]) -> Optional[str]:
        """
        Convert a relative path to an absolute path based on the application's base directory.
        
        Args:
            relative_path: Relative path to convert
            
        Returns:
            Absolute path or None if path is invalid
        """
        if not relative_path:
            return None
        
        # Fix common path issues
        relative_path = self.fix_path(relative_path)
        
        # Normalize path separators for consistency
        normalized_path = os.path.normpath(relative_path)
            
        # If it's already an absolute path and exists, return it
        if os.path.isabs(normalized_path):
            if os.path.exists(normalized_path):
                return normalized_path
        
        # Try different path combinations to find the file
        possible_paths = [
            normalized_path,  # As is
            os.path.join(config.BASE_DIR, normalized_path),  # Relative to base dir
            os.path.join(config.ASSETS_DIR, os.path.basename(normalized_path)),  # Just filename in assets
            os.path.join(config.PRODUCT_IMAGES_DIR, os.path.basename(normalized_path))  # Just filename in product_images
        ]
        
        # If path starts with 'assets/', try without that prefix too
        parts = normalized_path.split(os.path.sep)
        if parts and parts[0] == 'assets':
            without_assets = os.path.sep.join(parts[1:])  # Remove 'assets/' prefix
            possible_paths.append(os.path.join(config.BASE_DIR, without_assets))
            # If nested, also try just the filename
            if len(parts) > 2:
                just_filename = parts[-1]
                possible_paths.append(os.path.join(config.ASSETS_DIR, just_filename))
                possible_paths.append(os.path.join(config.PRODUCT_IMAGES_DIR, just_filename))
            
        # Check all possible paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # If we get here, none of the paths worked
        return None
    
    def get_safe_image_path(self, product_name: str) -> str:
        """
        Generate a safe file path for a product image.
        
        Args:
            product_name: Name of the product
            
        Returns:
            Safe file path for the product image
        """
        # Create a safe filename from the product name
        safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        image_path = os.path.join(config.PRODUCT_IMAGES_DIR, f"{safe_name}.jpg")
            
        return image_path
    
    def save_product_image(self, source_path: str, product_name: str) -> str:
        """
        Save a product image to the images directory.
        
        Args:
            source_path: Path to source image
            product_name: Name of the product
            
        Returns:
            Path to the saved image or default image
        """
        # Validate source path
        if not source_path:
            return self.default_image_path
        
        if not os.path.exists(source_path):
            return self.default_image_path
            
        try:
            # Get destination path
            dest_path = self.get_safe_image_path(product_name)
            
            # Check if destination directory exists
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Open and process the image
            with Image.open(source_path) as img:
                img = img.convert('RGB')
                
                # Get original image size
                original_size = img.size
                
                # Resize if too large
                if original_size[0] > 800 or original_size[1] > 800:
                    img.thumbnail((800, 800))
                
                # Save image
                img.save(dest_path, 'JPEG', quality=85)
                
            return dest_path
        except Exception as e:
            print(f"Error saving image: {e}")
            return self.default_image_path
    
    def load_product_image(self, image_path: Optional[str], size: Tuple[int, int] = (200, 200), master=None) -> ImageTk.PhotoImage:
        """
        Load a product image and resize it.
        
        Args:
            image_path: Path to the image
            size: Tuple with width and height
            master: Tkinter Master Window
        Returns:
            ImageTk.PhotoImage: Image object for Tkinter
        """
        # Create a cache key from the image path and size
        cache_key = f"{image_path}_{size[0]}x{size[1]}_{id(master)}"
        
        # Return cached image if available
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
                
        # If we have a pre-loaded default photo and no image path, use it directly
        if not image_path:
            # Always create a fresh PhotoImage from the default image file
            try:
                with Image.open(self.default_image_path) as img:
                    img = img.convert('RGB')
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                    self._image_cache[cache_key] = photo
                    return photo
            except Exception as e:
                print(f"Error creating default image: {e}")
                # Last resort fallback
                img = Image.new('RGB', size, color='gray')
                photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                self._image_cache[cache_key] = photo
                return photo
        
        try:
            # Get absolute path
            absolute_path = self.get_absolute_path(image_path)
            
            # If path couldn't be found, use default
            if not absolute_path:
                # If default is already loaded and cached, use it
                if self._default_photo:
                    self._image_cache[cache_key] = self._default_photo
                    return self._default_photo
                    
                # Otherwise, load default image
                with Image.open(self.default_image_path) as img:
                    img = img.convert('RGB')
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                    self._image_cache[cache_key] = photo
                    return photo
            
            # Check if file exists
            if not os.path.exists(absolute_path):
                raise FileNotFoundError(f"Image file not found: {absolute_path}")
            
            # Load the custom image
            with Image.open(absolute_path) as img:
                img = img.convert('RGB')
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                self._image_cache[cache_key] = photo
                return photo
                
        except Exception as e:
            print(f"Error loading image '{image_path}': {e}")
            
            # Return default photo if we have it
            if self._default_photo:
                self._image_cache[cache_key] = self._default_photo
                return self._default_photo
                
            # Try to load the default image as a last resort
            try:
                with Image.open(self.default_image_path) as img:
                    img = img.convert('RGB')
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                    self._image_cache[cache_key] = photo
                    return photo
            except Exception as e2:
                print(f"Critical error loading default image: {e2}")
                
                # Create an empty image as last resort
                img = Image.new('RGB', size, color='gray')
                photo = ImageTk.PhotoImage(img, master=master)  # Pass master parameter here
                self._image_cache[cache_key] = photo
                return photo
    
    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._image_cache.clear()
        
        # Reload the default image
        self._default_photo = self._load_default_image((200, 200))
    
    def delete_product_image(self, image_path: Optional[str]) -> None:
        """
        Delete a product image file.
        
        Args:
            image_path: Path to the image to delete
        """
        if not image_path:
            return
            
        if image_path == self.default_image_path:
            return
            
        # Fix the path if needed
        image_path = self.fix_path(image_path)
        
        # Check if the file exists
        if not os.path.exists(image_path):
            # Try to get the absolute path
            absolute_path = self.get_absolute_path(image_path)
            if absolute_path and os.path.exists(absolute_path):
                image_path = absolute_path
            else:
                return
        
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image: {e}")

# Singleton instance
_image_handler = None

def get_image_handler() -> ImageHandler:
    """Get the singleton instance of ImageHandler."""
    global _image_handler
    
    if _image_handler is None:
        _image_handler = ImageHandler()
        
    return _image_handler