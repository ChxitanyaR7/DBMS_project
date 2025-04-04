# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # Better secret key handling

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Chxitanya_7'),  # Make sure this matches your MySQL password
    'database': os.environ.get('DB_NAME', 'product_db')
}

# Low stock threshold
LOW_STOCK_THRESHOLD = int(os.environ.get('LOW_STOCK_THRESHOLD', 5))
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        try:
            # Connect to database
            db = get_db()
            if not db:
                flash('Database connection error', 'danger')
                return render_template('login.html')
            
            cursor = db.cursor(dictionary=True)  # Return results as dictionaries
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            db.close()
            
            if user and check_password_hash(user['password_hash'], password):
                # Login successful
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('signup.html')
        
        try:
            # Connect to database
            db = get_db()
            if not db:
                flash('Database connection error', 'danger')
                return render_template('signup.html')
            
            cursor = db.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s", 
                          (username, email))
            if cursor.fetchone()[0] > 0:
                flash('Username or email already exists', 'danger')
                cursor.close()
                db.close()
                return render_template('signup.html')
            
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Add user to database
            cursor.execute("""
                INSERT INTO users (username, email, password_hash) 
                VALUES (%s, %s, %s)
            """, (username, email, password_hash))
            
            db.commit()
            cursor.close()
            db.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Log out the current user"""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        if not session.get('is_admin', False):
            flash('Admin privileges required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Database connection function
def get_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Database connection successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        # If database doesn't exist, try to create it
        if err.errno == 1049:  # Unknown database
            try:
                print("Attempting to create database...")
                db_config_copy = DB_CONFIG.copy()
                db_name = db_config_copy.pop('database')
                
                conn = mysql.connector.connect(**db_config_copy)
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                cursor.close()
                conn.close()
                
                # Try connection again
                return mysql.connector.connect(**DB_CONFIG)
            except mysql.connector.Error as nested_err:
                print(f"Failed to create database: {nested_err}")
                return None
        return None

# Initialize database
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
                # In the init_db() function, add this after your other CREATE TABLE statements:
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
        
        
        # Insert default category if none exists
        cursor.execute("SELECT COUNT(*) FROM categories")
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO categories (name) VALUES ('General')")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
        return False

# Get categories
def get_categories():
    try:
        db = get_db()
        if not db:
            return []
        
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cursor.fetchall()
        cursor.close()
        db.close()
        return categories
    except mysql.connector.Error as err:
        print(f"Error fetching categories: {err}")
        return []

# Routes
@app.route('/')
def index():
    try:
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return render_template('index.html', products=[], low_stock_products=[])
        
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.price, p.quantity, c.name as category_name, 
                p.created_at, p.updated_at
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.name
        """)
        products = cursor.fetchall()
        
        # Check for low stock
        low_stock_products = [p for p in products if p[3] < LOW_STOCK_THRESHOLD]
        
        cursor.close()
        db.close()
        return render_template('index.html', products=products, low_stock_products=low_stock_products)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('index.html', products=[], low_stock_products=[])

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            category_id = request.form.get('category_id') or None
            
            if price < 0:
                flash('Price cannot be negative', 'danger')
                return redirect(url_for('add_product'))
            
            if quantity < 0:
                flash('Quantity cannot be negative', 'danger')
                return redirect(url_for('add_product'))
            
            db = get_db()
            if not db:
                flash('Database connection error', 'danger')
                return redirect(url_for('index'))
            
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO products (name, price, quantity, category_id)
                VALUES (%s, %s, %s, %s)
            """, (name, price, quantity, category_id))
            db.commit()
            
            # Check if we need to issue a low stock warning
            if quantity < LOW_STOCK_THRESHOLD:
                flash(f'Warning: {name} has been added with low stock ({quantity} items)', 'warning')
            
            cursor.close()
            db.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('add_product'))
    
    categories = get_categories()
    return render_template('add.html', categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    try:
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
        
        cursor = db.cursor()
        
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            category_id = request.form.get('category_id') or None
            
            if price < 0:
                flash('Price cannot be negative', 'danger')
                return redirect(url_for('edit_product', id=id))
            
            if quantity < 0:
                flash('Quantity cannot be negative', 'danger')
                return redirect(url_for('edit_product', id=id))
            
            cursor.execute("""
                UPDATE products 
                SET name=%s, price=%s, quantity=%s, category_id=%s, updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
            """, (name, price, quantity, category_id, id))
            db.commit()
            
            # Check if we need to issue a low stock warning
            if quantity < LOW_STOCK_THRESHOLD:
                flash(f'Warning: {name} has low stock ({quantity} items)', 'warning')
            
            flash('Product updated successfully!', 'success')
            return redirect(url_for('index'))
        
        cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """, (id,))
        product = cursor.fetchone()
        
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('index'))
        
        categories = get_categories()
        cursor.close()
        db.close()
        return render_template('edit.html', product=product, categories=categories)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    try:
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return render_template('categories.html', categories=[])
        
        cursor = db.cursor()
        
        if request.method == 'POST':
            category_name = request.form['name']
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
            db.commit()
            flash('Category added successfully!', 'success')
        
        cursor.execute("""
            SELECT c.id, c.name, COUNT(p.id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id
            ORDER BY c.name
        """)
        categories = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('categories.html', categories=categories)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('categories.html', categories=[])

@app.route('/delete_category/<int:id>')
def delete_category(id):
    try:
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return redirect(url_for('manage_categories'))
        
        cursor = db.cursor()
        
        # Check if category has products
        cursor.execute("SELECT COUNT(*) FROM products WHERE category_id = %s", (id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash(f'Cannot delete category with {count} associated products', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Get category name for the success message
        cursor.execute("SELECT name FROM categories WHERE id = %s", (id,))
        category = cursor.fetchone()
        
        if not category:
            flash('Category not found', 'danger')
            return redirect(url_for('manage_categories'))
        
        cursor.execute("DELETE FROM categories WHERE id = %s", (id,))
        db.commit()
        cursor.close()
        db.close()
        flash(f'Category "{category[0]}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('manage_categories'))

@app.route('/search')
def search_products():
    try:
        query = request.args.get('query', '')
        
        if not query:
            return redirect(url_for('index'))
        
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
        
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.price, p.quantity, c.name as category_name, 
                p.created_at, p.updated_at
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE %s OR c.name LIKE %s
            ORDER BY p.name
        """, (f'%{query}%', f'%{query}%'))
        
        products = cursor.fetchall()
        cursor.close()
        db.close()
        
        return render_template('search_results.html', products=products, query=query)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/update_stock/<int:id>', methods=['POST'])
def update_stock(id):
    try:
        operation = request.form.get('operation')
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Quantity must be positive', 'danger')
            return redirect(url_for('index'))
        
        db = get_db()
        if not db:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
        
        cursor = db.cursor()
        
        # Get current product info
        cursor.execute("SELECT name, quantity FROM products WHERE id = %s", (id,))
        product = cursor.fetchone()
        
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('index'))
        
        product_name, current_quantity = product
        
        if operation == 'add':
            new_quantity = current_quantity + quantity
            cursor.execute(
                "UPDATE products SET quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", 
                (new_quantity, id)
            )
            flash(f'Added {quantity} units to {product_name}. New stock: {new_quantity}', 'success')
        elif operation == 'remove':
            if current_quantity < quantity:
                flash(f'Cannot remove {quantity} units. Only {current_quantity} in stock.', 'danger')
            else:
                new_quantity = current_quantity - quantity
                cursor.execute(
                    "UPDATE products SET quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", 
                    (new_quantity, id)
                )
                flash(f'Removed {quantity} units from {product_name}. New stock: {new_quantity}', 'success')
                
                # Check if we need to issue a low stock warning
                if new_quantity < LOW_STOCK_THRESHOLD:
                    flash(f'Warning: {product_name} now has low stock ({new_quantity} items)', 'warning')
        
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

def create_admin_user(username, email, password):
    try:
        db = get_db()
        if not db:
            print("Database connection error")
            return False
        
        cursor = db.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s", 
                      (username, email))
        if cursor.fetchone()[0] > 0:
            print("Admin user already exists")
            cursor.close()
            db.close()
            return False
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Add admin user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin) 
            VALUES (%s, %s, %s, TRUE)
        """, (username, email, password_hash))
        
        db.commit()
        cursor.close()
        db.close()
        print(f"Admin user '{username}' created successfully")
        return True
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return False

if __name__ == '__main__':
    # Initialize database when the app starts
    if init_db():
        print("Database initialized successfully")
    else:
        print("Failed to initialize database")
    
    app.run(debug=True)