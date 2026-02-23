"""
User Management Module
Handles user and role operations.
"""

import hashlib
from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager
import config


class RoleManager:
    """Manages user roles."""
    
    def __init__(self):
        """Initialize the role manager."""
        self.db_manager = get_db_manager()
    
    def get_all_roles(self) -> List[Tuple]:
        """Retrieve all roles from the database.
        
        Returns:
            List of role tuples (id, role_name)
        """
        try:
            self.db_manager.users_db.execute("SELECT id, role_name FROM roles")
            return self.db_manager.users_db.fetchall()
        except Exception as e:
            print(f"Error fetching roles: {str(e)}")
            return []
    
    def get_role_by_id(self, role_id: int) -> Optional[Tuple]:
        """Retrieve a role by its ID.
        
        Args:
            role_id: ID of the role to retrieve
            
        Returns:
            Role tuple or None if not found
        """
        try:
            self.db_manager.users_db.execute("SELECT * FROM roles WHERE id=?", (role_id,))
            return self.db_manager.users_db.fetchone()
        except Exception as e:
            print(f"Error fetching role: {str(e)}")
            return None
    
    def add_role(self, role_name: str) -> Tuple[bool, str]:
        """Add a new role to the database.
        
        Args:
            role_name: Name of the new role
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if role already exists
            self.db_manager.users_db.execute("SELECT id FROM roles WHERE role_name=?", (role_name,))
            if self.db_manager.users_db.fetchone():
                return False, f"Role '{role_name}' already exists"
            
            # Add the new role
            self.db_manager.users_db.execute("INSERT INTO roles (role_name) VALUES (?)", (role_name,))
            self.db_manager.commit_users()
            return True, f"Role '{role_name}' added successfully"
        except Exception as e:
            return False, f"Error adding role: {str(e)}"
    
    def update_role(self, role_id: int, new_role_name: str) -> Tuple[bool, str]:
        """Update an existing role.
        
        Args:
            role_id: ID of the role to update
            new_role_name: New name for the role
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if role name already exists for another role
            self.db_manager.users_db.execute(
                "SELECT id FROM roles WHERE role_name=? AND id!=?", 
                (new_role_name, role_id)
            )
            if self.db_manager.users_db.fetchone():
                return False, f"Role '{new_role_name}' already exists"
            
            # Update the role
            self.db_manager.users_db.execute(
                "UPDATE roles SET role_name=? WHERE id=?", 
                (new_role_name, role_id)
            )
            self.db_manager.commit_users()
            return True, f"Role updated successfully"
        except Exception as e:
            return False, f"Error updating role: {str(e)}"
    
    def delete_role(self, role_id: int) -> Tuple[bool, str]:
        """Delete a role from the database.
        
        Args:
            role_id: ID of the role to delete
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if role is associated with any users
            self.db_manager.users_db.execute("SELECT COUNT(*) FROM users WHERE role_id=?", (role_id,))
            count = self.db_manager.users_db.fetchone()[0]
            
            if count > 0:
                return False, f"Cannot delete role: {count} users are assigned to this role"
            
            # Delete the role
            self.db_manager.users_db.execute("DELETE FROM roles WHERE id=?", (role_id,))
            self.db_manager.commit_users()
            return True, "Role deleted successfully"
        except Exception as e:
            return False, f"Error deleting role: {str(e)}"
    
    def initialize_default_roles(self) -> None:
        """Initialize default roles if no roles exist in the database."""
        try:
            # Check if there are any roles
            self.db_manager.users_db.execute("SELECT COUNT(*) FROM roles")
            count = self.db_manager.users_db.fetchone()[0]
            
            if count == 0:
                # Add default roles
                for role in config.DEFAULT_ROLES:
                    self.db_manager.users_db.execute(
                        "INSERT INTO roles (role_name) VALUES (?)", (role,)
                    )
                
                self.db_manager.commit_users()
                print("Default roles initialized")
        except Exception as e:
            print(f"Error initializing default roles: {str(e)}")

import hashlib
from typing import List, Tuple, Optional, Dict, Any

from models.database import get_db_manager
import config

class UserManager:
    """Manages user operations."""
    
    def __init__(self):
        """Initialize the user manager."""
        self.db_manager = get_db_manager()
    
    def add_user(self, username: str, password: str, role_id: int) -> Tuple[bool, str]:
        """Add a new user to the database.
        
        Args:
            username: Username for the new user
            password: Password (will be hashed)
            role_id: Role ID for the user
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Hash the password
            password_hash = self._hash_password(password)
            
            # Check if username already exists
            self.db_manager.users_db.execute(
                "SELECT id FROM users WHERE username=?", 
                (username,)
            )
            if self.db_manager.users_db.fetchone():
                return False, "Username already exists"
            
            # Insert the user
            self.db_manager.users_db.execute(
                "INSERT INTO users (username, password, role_id) VALUES (?, ?, ?)", 
                (username, password_hash, role_id)
            )
            self.db_manager.commit_users()
            
            return True, "User successfully added"
        except Exception as e:
            return False, f"Error adding user: {str(e)}"
    
    def update_user(self, user_id: int, username: str, password: Optional[str], role_id: int) -> Tuple[bool, str]:
        """Update an existing user in the database.
        
        Args:
            user_id: ID of the user to update
            username: New username
            password: New password (None to keep current)
            role_id: New role ID
            
        Returns:
            Tuple containing success status and message
        """
        try:
            # Check if username already exists for another user
            self.db_manager.users_db.execute(
                "SELECT id FROM users WHERE username=? AND id!=?", 
                (username, user_id)
            )
            if self.db_manager.users_db.fetchone():
                return False, "Username already exists"
            
            if password:
                # Hash the new password
                password_hash = self._hash_password(password)
                
                # Update user with new password
                self.db_manager.users_db.execute(
                    "UPDATE users SET username=?, password=?, role_id=? WHERE id=?",
                    (username, password_hash, role_id, user_id)
                )
            else:
                # Update user without changing password
                self.db_manager.users_db.execute(
                    "UPDATE users SET username=?, role_id=? WHERE id=?",
                    (username, role_id, user_id)
                )
            
            self.db_manager.commit_users()
            return True, "User updated successfully"
        except Exception as e:
            return False, f"Error updating user: {str(e)}"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user from the database.
        
        Args:
            username: Username of the user to delete
            
        Returns:
            Tuple containing success status and message
        """
        try:
            self.db_manager.users_db.execute(
                "DELETE FROM users WHERE username=?", 
                (username,)
            )
            
            if self.db_manager.users_db.cursor.rowcount == 0:
                return False, "User not found"
                
            self.db_manager.commit_users()
            return True, "User successfully removed"
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"
    
    def get_user_by_id(self, user_id: int) -> Optional[Tuple]:
        """Retrieve a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User tuple or None if not found
        """
        try:
            self.db_manager.users_db.execute(
                "SELECT * FROM users WHERE id=?", 
                (user_id,)
            )
            return self.db_manager.users_db.fetchone()
        except Exception as e:
            print(f"Error fetching user: {str(e)}")
            return None
    
    def get_all_users(self) -> List[Tuple]:
        """Retrieve all users with their role information.
        
        Returns:
            List of user tuples with role data
        """
        try:
            self.db_manager.users_db.execute("""
                SELECT u.id, u.username, u.password, u.role_id, r.role_name 
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
            """)
            return self.db_manager.users_db.fetchall()
        except Exception as e:
            print(f"Error fetching users: {str(e)}")
            return []
        
    def has_users(self) -> bool:
        """Check if any users exist in the database.
        
        Returns:
            True if at least one user exists, False otherwise
        """
        try:
            self.db_manager.users_db.execute("SELECT COUNT(*) FROM users")
            result = self.db_manager.users_db.fetchone()
            return result and result[0] > 0
        except Exception as e:
            print(f"Error checking if users exist: {str(e)}")
            return False
    
    def verify_login(self, username: str, password: str) -> Tuple[bool, Optional[int]]:
        """Verify login credentials.
        
        Args:
            username: Username to verify
            password: Password to verify
            
        Returns:
            Tuple containing (is_valid, user_id)
        """
        try:
            # Hash the password
            password_hash = self._hash_password(password)
            
            # Check credentials
            self.db_manager.users_db.execute(
                "SELECT id FROM users WHERE username=? AND password=?", 
                (username, password_hash)
            )
            user = self.db_manager.users_db.fetchone()
            
            if user:
                return True, user[0]
            else:
                return False, None
        except Exception as e:
            print(f"Error verifying login: {str(e)}")
            return False, None
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256.
        
        Args:
            password: Password to hash
            
        Returns:
            Hexadecimal string of hashed password
        """
        sha256 = hashlib.sha256()
        sha256.update(password.encode())
        return sha256.hexdigest()