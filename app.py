# Flask CRUD Application

from flask import Flask, request, redirect, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Configure database connection
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'crud_app')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize MySQL connection
mysql = MySQL(app)

# HTML TEMPLATES (stored as strings for simplicity)

REGISTER_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Register - CRUD App</title>
    <style>
        * { margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 20px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }
        button { width: 100%; padding: 10px; margin: 20px 0; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin: 10px 0; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="password" name="password" placeholder="Password (min 6 chars)" required minlength="6">
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login here</a></p>
    </div>
</body>
</html>
'''

LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - CRUD App</title>
    <style>
        * { margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 20px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }
        button { width: 100%; padding: 10px; margin: 20px 0; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form method="POST">
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/register">Register here</a></p>
    </div>
</body>
</html>
'''


# ============================================================================
# ROUTE 1: HOME PAGE
# ============================================================================

@app.route('/')
def index():
    """
    Home page - redirects to dashboard if logged in, otherwise to login
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ============================================================================
# ROUTE 2: REGISTRATION
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration page
    GET: Show registration form
    POST: Process registration form
    """

    if request.method == 'POST':
        # Get data from HTML form
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if all fields are filled
        if not name or not email or not password:
            return "Error: Please fill all fields", 400

        # Check password length
        if len(password) < 6:
    

            # Redirect to login page
            return redirect(url_for('login'))

        except Exception as e:
            return f"Error: {str(e)}", 500

    # Show registration form (GET request)
    return REGISTER_PAGE


# ============================================================================
# ROUTE 3: LOGIN
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page
    GET: Show login form
    POST: Process login
    """

    if request.method == 'POST':
        # Get data from form
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if fields are filled
        if not email or not password:
            return "Error: Please fill all fields", 400

        try:
            # Connect to database and find user
            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT id, password, name FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            cursor.close()

            # Check if user exists and password is correct
            if user and check_password_hash(user[1], password):
                # Create session (like a login cookie)
                session['user_id'] = user[0]
                session['user_name'] = user[2]
                session['user_email'] = email

                # Redirect to dashboard
                return redirect(url_for('dashboard'))

            return "Error: Invalid email or password", 401

        except Exception as e:
            return f"Error: {str(e)}", 500

    # Show login form (GET request)
    return LOGIN_PAGE


# ============================================================================
# ROUTE 4: DASHBOARD - Show user's items
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """
    Main dashboard - shows user's items and form to add new items
    Only accessible if user is logged in
    """

    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        # Get all items for this user from database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, title, description FROM items WHERE user_id = %s ORDER BY id DESC",
            (session['user_id'],)
        )
        items = cursor.fetchall()
        cursor.close()

        # Build HTML table with items
        items_html = ""
        if items:
            for item in items:
                items_html += f'''
                <tr>
                    <td>{item[1]}</td>
                    <td>{item[2] if item[2] else "-"}</td>
                    <td>
                        <a href="/edit/{item[0]}"><button type="button" style="padding:5px 10px; background:#28a745;">Edit</button></a>
                        <a href="/delete/{item[0]}"><button type="button" style="padding:5px 10px; background:#dc3545;">Delete</button></a>
                    </td>
                </tr>
                '''
        else:
            items_html = '<tr><td colspan="3" style="text-align:center;">No items yet. Add one below!</td></tr>'

        # Build and return full dashboard page
        dashboard_page = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - CRUD App</title>
            <style>
                * {{ margin: 0; padding: 0; }}
                body {{ font-family: Arial, sans-serif; background: #f0f0f0; }}
                .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
                .header {{ background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
                .header h1 {{ color: #333; }}
                .logout-btn {{ background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; text-decoration: none; }}
                .logout-btn:hover {{ background: #c82333; }}
                .card {{ background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .form-group {{ margin-bottom: 15px; }}
                input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 3px; font-family: Arial; }}
                textarea {{ height: 80px; }}
                .add-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }}
                .add-btn:hover {{ background: #0056b3; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th {{ background: #f0f0f0; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                a {{ text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome, {session['user_name']}! 👋</h1>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>

                <div class="card">
                    <h2>Add New Item</h2>
                    <form method="POST" action="/add-item">
                        <div class="form-group">
                            <input type="text" name="title" placeholder="Item Title (e.g., Buy groceries)" required>
                        </div>
                        <div class="form-group">
                            <textarea name="description" placeholder="Description (optional)"></textarea>
                        </div>
                        <button type="submit" class="add-btn">+ Add Item</button>
                    </form>
                </div>

                <div class="card">
                    <h2>Your Items</h2>
                    <table>
                        <tr>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                        {items_html}
                    </table>
                </div>
            </div>
        </body>
        </html>
        '''

        return dashboard_page

    except Exception as e:
        return f"Error: {str(e)}", 500


# ============================================================================
# ROUTE 5: ADD ITEM
# ============================================================================

@app.route('/add-item', methods=['POST'])
def add_item():
    """
    Add new item to database
    Only accessible if user is logged in
    """

    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get form data
    title = request.form.get('title')
    description = request.form.get('description')

    # Check if title is provided
    if not title:
        return "Error: Title is required", 400

    try:
        # Insert into database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO items (user_id, title, description) VALUES (%s, %s, %s)",
            (session['user_id'], title, description)
        )
        mysql.connection.commit()
        cursor.close()

        # Redirect back to dashboard
        return redirect(url_for('dashboard'))

    except Exception as e:
        return f"Error: {str(e)}", 500


# ============================================================================
# ROUTE 6: EDIT ITEM
# ============================================================================

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    """
    Edit existing item
    GET: Show edit form
    POST: Save changes
    """

    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor()

        # Get item from database (check that user owns it)
        cursor.execute(
            "SELECT id, title, description FROM items WHERE id = %s AND user_id = %s",
            (item_id, session['user_id'])
        )
        item = cursor.fetchone()

        # Item not found or user doesn't own it
        if not item:
            return "Error: Item not found or access denied", 404

        # Handle form submission
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')

            if not title:
                return "Error: Title is required", 400

            # Update database
            cursor.execute(
                "UPDATE items SET title = %s, description = %s WHERE id = %s AND user_id = %s",
                (title, description, item_id, session['user_id'])
            )
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('dashboard'))

        cursor.close()

        # Show edit form
        edit_page = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Edit Item - CRUD App</title>
            <style>
                * {{ margin: 0; padding: 0; }}
                body {{ font-family: Arial, sans-serif; background: #f0f0f0; }}
                .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 30px; border-radius: 5px; }}
                h1 {{ color: #333; margin-bottom: 20px; }}
                input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }}
                textarea {{ height: 100px; }}
                button {{ width: 100%; padding: 10px; margin: 10px 0; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; }}
                button:hover {{ background: #218838; }}
                a {{ color: #007bff; margin-top: 10px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Edit Item</h1>
                <form method="POST">
                    <input type="text" name="title" value="{item[1]}" required>
                    <textarea name="description">{item[2] if item[2] else ""}</textarea>
                    <button type="submit">Save Changes</button>
                </form>
                <a href="/dashboard">← Back to Dashboard</a>
            </div>
        </body>
        </html>
        '''

        return edit_page

    except Exception as e:
        return f"Error: {str(e)}", 500


# ============================================================================
# ROUTE 7: DELETE ITEM
# ============================================================================

@app.route('/delete/<int:item_id>')
def delete(item_id):
    """
    Delete item from database
    Only allow deletion if user owns the item
    """

    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor()

        # Delete item (only if user owns it)
        cursor.execute(
            "DELETE FROM items WHERE id = %s AND user_id = %s",
            (item_id, session['user_id'])
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard'))

    except Exception as e:
        return f"Error: {str(e)}", 500


# ============================================================================
# ROUTE 8: LOGOUT
# ============================================================================

@app.route('/logout')
def logout():
    """
    Logout user - clear session
    """
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Page not found error"""
    return "Error 404: Page not found", 404


@app.errorhandler(500)
def server_error(error):
    """Server error"""
    return "Error 500: Server error", 500


# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == '__main__':
    # debug=True: Shows errors and auto-reloads on code changes
    # host='0.0.0.0': Accessible from any IP (not just localhost)
    # port=5000: Runs on http://localhost:5000
    app.run(debug=True, host='0.0.0.0', port=5000)
