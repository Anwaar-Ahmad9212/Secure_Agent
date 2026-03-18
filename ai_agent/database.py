"""
database.py - SQLite database for demonstration
Contains realistic customer data that can be attacked
"""
import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "demo_database.db")


def init_database():
    """Initialize database with sample data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            credit_card TEXT,
            balance REAL,
            created_at TEXT
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product TEXT,
            amount REAL,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        # Insert sample customer data
        sample_customers = [
            ("Alice Johnson", "alice@email.com", "555-0101", "4532-1234-5678-9012", 1250.50),
            ("Bob Smith", "bob@email.com", "555-0102", "4532-9876-5432-1098", 3420.75),
            ("Carol White", "carol@email.com", "555-0103", "4532-5555-6666-7777", 890.25),
            ("David Brown", "david@email.com", "555-0104", "4532-1111-2222-3333", 5670.00),
            ("Eve Davis", "eve@email.com", "555-0105", "4532-4444-5555-6666", 2100.80),
        ]
        
        for name, email, phone, cc, balance in sample_customers:
            cursor.execute("""
                INSERT INTO customers (name, email, phone, credit_card, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, phone, cc, balance, datetime.now().isoformat()))
        
        # Insert sample orders
        sample_orders = [
            (1, "Laptop", 899.99, "completed"),
            (1, "Mouse", 25.50, "completed"),
            (2, "Monitor", 299.99, "pending"),
            (3, "Keyboard", 79.99, "completed"),
            (4, "Headphones", 149.99, "shipped"),
            (5, "Webcam", 89.99, "completed"),
        ]
        
        for cust_id, product, amount, status in sample_orders:
            cursor.execute("""
                INSERT INTO orders (customer_id, product, amount, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (cust_id, product, amount, status, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_FILE}")


def execute_query(query):
    """Execute a SQL query and return results."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        # Check if this is a SELECT query
        if query.strip().upper().startswith("SELECT"):
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {
                "status": "success",
                "rows": results,
                "count": len(results)
            }
        else:
            # For INSERT, UPDATE, DELETE
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return {
                "status": "success",
                "affected_rows": affected,
                "message": f"Query executed successfully. {affected} row(s) affected."
            }
    
    except sqlite3.Error as e:
        conn.close()
        return {
            "status": "error",
            "message": str(e)
        }


def get_all_customers():
    """Get all customers (safe query)."""
    return execute_query("SELECT id, name, email, phone, balance FROM customers")


def get_all_data():
    """DANGEROUS: Get all data including sensitive info."""
    return execute_query("SELECT * FROM customers")


def search_customer(name):
    """Search for a customer by name."""
    query = f"SELECT id, name, email, phone, balance FROM customers WHERE name LIKE '%{name}%'"
    return execute_query(query)


# Initialize on import
if not os.path.exists(DB_FILE):
    init_database()
