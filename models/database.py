"""
Database Management Module
Handles database connections and provides a foundation for all database operations.
"""

import sqlite3
from typing import Optional, Tuple, List, Dict, Any, Union, Callable

import config

class Database:
    """Base database connection class that handles common database operations."""
    
    def __init__(self, db_path: str):
        """Initialize a database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect()
    
    def connect(self) -> bool:
        """Establish a connection to the database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_path}: {e}")
            return False
    
    def ensure_connection(self) -> bool:
        """Ensure the database connection is active.
        
        Returns:
            True if connection is active, False otherwise
        """
        if self.connection is None or self.cursor is None:
            return self.connect()
        
        try:
            # Test the connection
            self.cursor.execute("SELECT 1")
            return True
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            return self.connect()
    
    def execute(self, query: str, params: Union[tuple, List[Any]] = ()) -> Optional[sqlite3.Cursor]:
        """Execute a query with parameters.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor object or None if execution failed
        """
        try:
            self.ensure_connection()
            if isinstance(params, list):
                return self.cursor.executemany(query, params)
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
    
    def executemany(self, query: str, param_list: List[tuple]) -> Optional[sqlite3.Cursor]:
        """Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query string
            param_list: List of parameter tuples
            
        Returns:
            Cursor object or None if execution failed
        """
        try:
            self.ensure_connection()
            return self.cursor.executemany(query, param_list)
        except sqlite3.Error as e:
            print(f"Error executing bulk query: {e}")
            return None
    
    def fetchone(self) -> Optional[tuple]:
        """Fetch a single row from the last query.
        
        Returns:
            Single row as tuple or None
        """
        try:
            return self.cursor.fetchone() if self.cursor else None
        except sqlite3.Error as e:
            print(f"Error fetching row: {e}")
            return None
    
    def fetchall(self) -> List[tuple]:
        """Fetch all rows from the last query.
        
        Returns:
            List of rows as tuples
        """
        try:
            return self.cursor.fetchall() if self.cursor else []
        except sqlite3.Error as e:
            print(f"Error fetching all rows: {e}")
            return []
    
    def commit(self) -> bool:
        """Commit changes to the database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.connection:
                self.connection.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error committing changes: {e}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        self.ensure_connection()
        self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        return self.fetchone() is not None


class DatabaseManager:
    """Manages connections to all application databases."""
    
    def __init__(self):
        """Initialize the database manager with connections to both databases."""
        self.pos_db = Database(config.DB_POS_PATH)
        self.users_db = Database(config.DB_USERS_PATH)
        self.initialize_schema()
    
    def initialize_schema(self) -> None:
        """Initialize the database schema if tables don't exist."""
        # POS database tables
        self._create_categories_table()
        self._create_suppliers_table()
        self._create_products_table()
        self._create_sales_table()
        
        # Users database tables
        self._create_roles_table()
        self._create_users_table()
        
        # Commit changes
        self.commit_all()
    
    def _create_categories_table(self) -> None:
        """Create the categories table if it doesn't exist."""
        self.pos_db.execute('''
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                discount INTEGER DEFAULT 0,
                image_path TEXT)
        ''')
    
    def _create_suppliers_table(self) -> None:
        """Create the suppliers table if it doesn't exist."""
        self.pos_db.execute('''
            CREATE TABLE IF NOT EXISTS suppliers(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact_info TEXT)
        ''')
    
    def _create_products_table(self) -> None:
        """Create the products table if it doesn't exist."""
        self.pos_db.execute('''
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category_id INTEGER,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                barcode TEXT UNIQUE,
                description TEXT,
                supplier_id INTEGER,
                discount INTEGER DEFAULT 0,
                unit_of_measurement TEXT DEFAULT 'unit',
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_alcoholic INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                image_path TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id))
        ''')
    
    def _create_sales_table(self) -> None:
        """Create the sales table if it doesn't exist."""
        self.pos_db.execute('''
            CREATE TABLE IF NOT EXISTS sales(
                id INTEGER PRIMARY KEY,
                transaction_id TEXT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                discount INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id))
        ''')
    
    def _create_roles_table(self) -> None:
        """Create the roles table if it doesn't exist."""
        self.users_db.execute('''
            CREATE TABLE IF NOT EXISTS roles(
                id INTEGER PRIMARY KEY,
                role_name TEXT NOT NULL)
        ''')
    
    def _create_users_table(self) -> None:
        """Create the users table if it doesn't exist."""
        self.users_db.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role_id INTEGER,
                FOREIGN KEY(role_id) REFERENCES roles(id))
        ''')
    
    def commit_pos(self) -> bool:
        """Commit changes to the POS database."""
        return self.pos_db.commit()
    
    def commit_users(self) -> bool:
        """Commit changes to the Users database."""
        return self.users_db.commit()
    
    def commit_all(self) -> None:
        """Commit changes to both databases."""
        self.commit_pos()
        self.commit_users()
    
    def close_all(self) -> None:
        """Close all database connections."""
        self.pos_db.close()
        self.users_db.close()


# Singleton instance for global use
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the singleton instance of DatabaseManager.
    
    Returns:
        The DatabaseManager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager