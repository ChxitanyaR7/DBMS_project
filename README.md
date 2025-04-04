# DBMS_project

Product Manager:
A simple web-based product management system built using Flask and MySQL. This application allows users to manage products, categories, and stock levels, with features like user authentication (signup/login), low stock alerts, and CRUD operations for products.

Features
User Authentication:

Signup and login functionality with password hashing for security.
Session management to track logged-in users.
Product Management:

Add, edit, and delete products.
Assign products to categories.
Update product stock levels.
Category Management:

Add and manage product categories.
Low Stock Alerts:

Automatically highlights products with low stock levels.
Responsive Design:

User-friendly interface for managing products and categories.
Technologies Used
Backend: Flask (Python)
Database: MySQL
Frontend: HTML, CSS, Bootstrap
Other Tools: Flask-WTF, Flask-Bcrypt, MySQL Connector

# Setup Instructions
1. Clone the Repository
```
git clone https://github.com/ChxitanyaR7/DBMS-project.git
cd DBMS-project
```

3. Install Dependencies
Make sure you have Python installed. Then, install the required Python packages:
```
pip install -r requirements.txt
```

4. Configure the Database
Create a MySQL database named product_db.
Update the database credentials in ```database.py```

5. Initialize the Database
Run the following script to create the necessary tables:
```
from database import init_db
init_db()
```

6. Run the Application
Start the Flask development server:
 ```
python app.py
```

8. Access the Application
Open your browser and navigate to:
 ```
http://127.0.0.1:5000
```

# File structure
```
your_project/
├── app.py
├── database.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   ├── categories.html
│   ├── login.html
│   ├── signup.html
│   ├── 404.html

```

## Features in Detail

### 1. User Authentication
- Users can sign up and log in securely.
- Passwords are hashed using Flask-Bcrypt for security.
- Session-based authentication ensures only logged-in users can access certain features.

### 2. Product Management
- Add new products with details like name, price, quantity, and category.
- Edit existing product details.
- Delete products from the database.
- Update stock levels with "Add Stock" and "Remove Stock" buttons.

### 3. Category Management
- Add and manage categories for products.
- Assign products to specific categories.

### 4. Low Stock Alerts
Products with stock levels below a predefined threshold (e.g., 5) are highlighted.
A warning message is displayed on the main page for low-stock products.

## Screenshots

### 1. Main Page
![Main Page](screenshots/main_page.png)

### 2. Login Page
![Login Page](screenshots/login_page.png)

### 3. Signup Page
![Signup Page](screenshots/signup_page.png)

## Future Enhancements
- Add user roles (e.g., admin, regular user).
- Implement search and filter functionality for products.
- Add pagination for large product lists.
- Integrate email notifications for low stock alerts.
  
## Contributing
Feel free to fork this repository and submit pull requests. Contributions are welcome!


