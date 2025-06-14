from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Data storage files
USERS_FILE = 'data/users.json'
DELIVERIES_FILE = 'data/deliveries.json'

def ensure_data_directory():
    """Ensure the data directory exists"""
    if not os.path.exists('data'):
        os.makedirs('data')

def load_users():
    """Load users from JSON file"""
    ensure_data_directory()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    ensure_data_directory()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_deliveries():
    """Load deliveries from JSON file"""
    ensure_data_directory()
    if os.path.exists(DELIVERIES_FILE):
        with open(DELIVERIES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_deliveries(deliveries):
    """Save deliveries to JSON file"""
    ensure_data_directory()
    with open(DELIVERIES_FILE, 'w') as f:
        json.dump(deliveries, f, indent=2)

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def customer_required(f):
    """Decorator to require customer role"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        if session.get('user_role') != 'customer':
            flash('Access denied. Customer privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def driver_required(f):
    """Decorator to require driver role"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        if session.get('user_role') != 'driver':
            flash('Access denied. Driver privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_type = request.form.get('user_type', '')
        
        # Validation
        if not all([name, email, password, user_type]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if user_type not in ['customer', 'driver']:
            flash('Invalid user type selected.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if email already exists
        users = load_users()
        if email in users:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Create new user
        user_id = str(uuid.uuid4())
        users[email] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'user_type': user_type,
            'created_at': datetime.now().isoformat()
        }
        
        save_users(users)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        
        users = load_users()
        user = users.get(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            session['user_role'] = user['user_type']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_role = session.get('user_role')
    deliveries = load_deliveries()
    
    if user_role == 'customer':
        # Show customer's deliveries
        user_deliveries = []
        for delivery_id, delivery in deliveries.items():
            if delivery['customer_id'] == session['user_id']:
                user_deliveries.append(delivery)
        
        # Sort by created_at (newest first)
        user_deliveries.sort(key=lambda x: x['created_at'], reverse=True)
        return render_template('customer_dashboard.html', deliveries=user_deliveries)
    
    elif user_role == 'driver':
        # Show available and assigned deliveries
        available_deliveries = []
        assigned_deliveries = []
        
        for delivery_id, delivery in deliveries.items():
            if delivery['status'] == 'Pending':
                available_deliveries.append(delivery)
            elif delivery.get('driver_id') == session['user_id']:
                assigned_deliveries.append(delivery)
        
        # Sort by created_at (newest first)
        available_deliveries.sort(key=lambda x: x['created_at'], reverse=True)
        assigned_deliveries.sort(key=lambda x: x['created_at'], reverse=True)
        
        return render_template('driver_dashboard.html', 
                             available_deliveries=available_deliveries,
                             assigned_deliveries=assigned_deliveries)
    
    return render_template('dashboard.html')

@app.route('/create_delivery', methods=['GET', 'POST'])
@customer_required
def create_delivery():
    """Create a new delivery request (customers only)"""
    if request.method == 'POST':
        pickup_address = request.form.get('pickup_address', '').strip()
        dropoff_address = request.form.get('dropoff_address', '').strip()
        package_note = request.form.get('package_note', '').strip()
        
        # Validation
        if not all([pickup_address, dropoff_address, package_note]):
            flash('All fields are required.', 'error')
            return render_template('create_delivery.html')
        
        # Create delivery
        delivery_id = str(uuid.uuid4())
        deliveries = load_deliveries()
        
        deliveries[delivery_id] = {
            'id': delivery_id,
            'customer_id': session['user_id'],
            'customer_name': session['user_name'],
            'pickup_address': pickup_address,
            'dropoff_address': dropoff_address,
            'package_note': package_note,
            'status': 'Pending',
            'created_at': datetime.now().isoformat(),
            'driver_id': None,
            'driver_name': None,
            'accepted_at': None,
            'completed_at': None
        }
        
        save_deliveries(deliveries)
        flash('Delivery request created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_delivery.html')

@app.route('/pending_deliveries')
@login_required
def pending_deliveries():
    """View all pending deliveries"""
    deliveries = load_deliveries()
    pending_deliveries = []
    
    for delivery_id, delivery in deliveries.items():
        if delivery['status'] == 'Pending':
            pending_deliveries.append(delivery)
    
    # Sort by created_at (newest first)
    pending_deliveries.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('pending_deliveries.html', deliveries=pending_deliveries)

@app.route('/accept_delivery/<delivery_id>')
@driver_required
def accept_delivery(delivery_id):
    """Accept a delivery (drivers only)"""
    deliveries = load_deliveries()
    
    if delivery_id not in deliveries:
        flash('Delivery not found.', 'error')
        return redirect(url_for('dashboard'))
    
    delivery = deliveries[delivery_id]
    
    if delivery['status'] != 'Pending':
        flash('This delivery is no longer available.', 'error')
        return redirect(url_for('dashboard'))
    
    # Assign delivery to driver
    delivery['driver_id'] = session['user_id']
    delivery['driver_name'] = session['user_name']
    delivery['status'] = 'Accepted'
    delivery['accepted_at'] = datetime.now().isoformat()
    
    save_deliveries(deliveries)
    flash('Delivery accepted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/complete_delivery/<delivery_id>')
@driver_required
def complete_delivery(delivery_id):
    """Mark delivery as completed (drivers only)"""
    deliveries = load_deliveries()
    
    if delivery_id not in deliveries:
        flash('Delivery not found.', 'error')
        return redirect(url_for('dashboard'))
    
    delivery = deliveries[delivery_id]
    
    if delivery.get('driver_id') != session['user_id']:
        flash('You can only complete your own deliveries.', 'error')
        return redirect(url_for('dashboard'))
    
    if delivery['status'] != 'Accepted':
        flash('This delivery cannot be completed.', 'error')
        return redirect(url_for('dashboard'))
    
    # Mark as completed
    delivery['status'] = 'Completed'
    delivery['completed_at'] = datetime.now().isoformat()
    
    save_deliveries(deliveries)
    flash('Delivery marked as completed!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delivery_details/<delivery_id>')
@login_required
def delivery_details(delivery_id):
    """View delivery details"""
    deliveries = load_deliveries()
    
    if delivery_id not in deliveries:
        flash('Delivery not found.', 'error')
        return redirect(url_for('dashboard'))
    
    delivery = deliveries[delivery_id]
    
    # Check if user has permission to view this delivery
    user_role = session.get('user_role')
    if user_role == 'customer' and delivery['customer_id'] != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    elif user_role == 'driver' and delivery.get('driver_id') != session['user_id'] and delivery['status'] == 'Pending':
        # Drivers can view pending deliveries and their own deliveries
        pass
    
    return render_template('delivery_details.html', delivery=delivery)

# API endpoints for real-time updates
@app.route('/api/deliveries/status')
@login_required
def api_delivery_status():
    """API endpoint to get delivery status updates"""
    deliveries = load_deliveries()
    user_role = session.get('user_role')
    result = []
    
    if user_role == 'customer':
        for delivery_id, delivery in deliveries.items():
            if delivery['customer_id'] == session['user_id']:
                result.append({
                    'id': delivery['id'],
                    'status': delivery['status'],
                    'driver_name': delivery.get('driver_name'),
                    'created_at': delivery['created_at']
                })
    elif user_role == 'driver':
        for delivery_id, delivery in deliveries.items():
            if delivery['status'] == 'Pending' or delivery.get('driver_id') == session['user_id']:
                result.append({
                    'id': delivery['id'],
                    'status': delivery['status'], 
                    'customer_name': delivery['customer_name'],
                    'created_at': delivery['created_at']
                })
    
    return jsonify(result)

if __name__ == '__main__':
    ensure_data_directory()
    app.run(debug=True)