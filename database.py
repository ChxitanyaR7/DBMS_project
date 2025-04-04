# This is a combined fix file - implement these changes in your project

# ===== database.py =====
import mysql.connector
import os
import time

def get_db_connection(retries=3, delay=2):
    """
    Attempt to connect to the database with retries
    """
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Chxitanya_7',  # Make sure this is your actual MySQL password
        'database': 'product_db',
        'raise_on_warnings': True,
        'connection_timeout': 10
    }
    
    for attempt in range(retries):
        try:
            print(f"Attempting database connection (attempt {attempt+1}/{retries})...")
            connection = mysql.connector.connect(**config)
            print("Database connection successful!")
            return connection
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            
            # If database doesn't exist, try to create it
            if err.errno == 1049:  # Unknown database
                try:
                    print("Database does not exist. Attempting to create...")
                    conn = mysql.connector.connect(
                        host=config['host'],
                        user=config['user'],
                        password=config['password']
                    )
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
                    cursor.close()
                    conn.close()
                    print(f"Database '{config['database']}' created successfully!")
                    # Don't return here, let the retry happen
                except mysql.connector.Error as create_err:
                    print(f"Failed to create database: {create_err}")
            
            # If this isn't the last attempt, wait before retrying
            if attempt < retries - 1:
                print(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
            else:
                print("Max connection attempts reached. Could not connect to database.")
                return None

# ===== Modify your app.py =====
# Replace your current get_db() function with this one:

def get_db():
    """Get database connection with error handling"""
    from database import get_db_connection
    return get_db_connection()

# ===== Initialize database =====
# Replace your init_db() function with this:

def init_db():

    
    """Initialize database tables"""
    try:
        # Get connection
        conn = get_db()
        if not conn:
            print("Could not initialize database: connection failed")
            return False
        
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create products table with proper foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INT DEFAULT 0,
                category_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)
        
        # Check if categories table is empty
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            print("Adding default category...")
            cursor.execute("INSERT INTO categories (name) VALUES ('General')")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
        return False