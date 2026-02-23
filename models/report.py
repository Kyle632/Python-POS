"""
Reports Management Module
Handles reporting and analytics.
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

from models.database import get_db_manager

class ReportManager:
    """Manages reporting and analytics."""
    
    def __init__(self):
        """Initialize the report manager."""
        self.db_manager = get_db_manager()
    
    def fetch_monthly_sales(self, month: int, year: int) -> float:
        """Fetch total sales for a specific month and year.
        
        Args:
            month: Month number (1-12)
            year: Year (e.g., 2023)
            
        Returns:
            Total sales amount for the month
        """
        start_date = f"{year}-{month:02d}-01"
        # Calculate end date (first day of next month)
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        self.db_manager.pos_db.execute(
            "SELECT SUM(total) FROM sales WHERE timestamp BETWEEN ? AND ?", 
            (start_date, end_date)
        )
        result = self.db_manager.pos_db.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def fetch_sales_by_category(self, start_date: str, end_date: str) -> List[Tuple[str, float]]:
        """Fetch sales grouped by product category.
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            List of tuples containing (category_name, total_sales)
        """
        self.db_manager.pos_db.execute("""
            SELECT c.name, SUM(s.total) 
            FROM sales s
            JOIN products p ON s.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE s.timestamp BETWEEN ? AND ?
            GROUP BY c.name
            ORDER BY SUM(s.total) DESC
        """, (start_date, end_date))
        
        return self.db_manager.pos_db.fetchall()
    
    def fetch_top_selling_products(self, limit: int = 10, 
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch top selling products by quantity.
        
        Args:
            limit: Number of products to return
            start_date: Optional start date in format 'YYYY-MM-DD'
            end_date: Optional end date in format 'YYYY-MM-DD'
            
        Returns:
            List of dictionaries containing product sales data
        """
        query = """
            SELECT p.id, p.name, SUM(s.quantity) as total_quantity, SUM(s.total) as total_sales
            FROM sales s
            JOIN products p ON s.product_id = p.id
        """
        
        params = []
        
        # Add date filtering if provided
        if start_date and end_date:
            query += " WHERE s.timestamp BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += """
            GROUP BY p.id
            ORDER BY total_quantity DESC
            LIMIT ?
        """
        
        params.append(limit)
        
        self.db_manager.pos_db.execute(query, params)
        results = self.db_manager.pos_db.fetchall()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'total_quantity': row[2],
                'total_sales': row[3]
            }
            for row in results
        ]
    
    def fetch_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Fetch products with stock below the specified threshold.
        
        Args:
            threshold: Stock threshold
            
        Returns:
            List of dictionaries containing low stock product data
        """
        self.db_manager.pos_db.execute("""
            SELECT p.id, p.name, p.stock, c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.stock <= ?
            ORDER BY p.stock ASC
        """, (threshold,))
        
        results = self.db_manager.pos_db.fetchall()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'stock': row[2],
                'category': row[3]
            }
            for row in results
        ]
    
    def fetch_daily_sales(self, days_limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch daily sales for the last specified number of days.
        
        Args:
            days_limit: Number of days to include
            
        Returns:
            List of dictionaries containing daily sales data
        """
        self.db_manager.pos_db.execute("""
            SELECT 
                date(timestamp) as sale_date, 
                SUM(total) as daily_total,
                COUNT(DISTINCT transaction_id) as transaction_count
            FROM sales
            GROUP BY date(timestamp)
            ORDER BY date(timestamp) DESC
            LIMIT ?
        """, (days_limit,))
        
        results = self.db_manager.pos_db.fetchall()
        
        return [
            {
                'date': row[0],
                'total': row[1],
                'transaction_count': row[2]
            }
            for row in results
        ]
    
    def fetch_sales_trend(self, period: str = 'monthly', limit: int = 12) -> List[Dict[str, Any]]:
        """Fetch sales trend data.
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            limit: Number of periods to include
            
        Returns:
            List of dictionaries containing trend data
        """
        if period == 'monthly':
            group_format = "strftime('%Y-%m', timestamp)"
        elif period == 'weekly':
            group_format = "strftime('%Y-%W', timestamp)"
        else:  # daily
            group_format = "date(timestamp)"
        
        query = f"""
            SELECT 
                {group_format} as period, 
                SUM(total) as period_total,
                COUNT(DISTINCT transaction_id) as transaction_count
            FROM sales
            GROUP BY {group_format}
            ORDER BY {group_format} DESC
            LIMIT ?
        """
        
        self.db_manager.pos_db.execute(query, (limit,))
        results = self.db_manager.pos_db.fetchall()
        
        return [
            {
                'period': row[0],
                'total': row[1],
                'transaction_count': row[2]
            }
            for row in results
        ]