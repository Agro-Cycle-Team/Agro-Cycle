import os
from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime

# ==============================
# APP INITIALIZATION
# ==============================

app = Flask(__name__)
app.config.from_object(Config)

# ==============================
# DATABASE CONNECTION
# ==============================

db = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

cursor = db.cursor(dictionary=True)

# ==============================
# HELPER FUNCTIONS
# ==============================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(role):
    def wrapper(func):
        def decorated(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect('/login')
            return func(*args, **kwargs)
        decorated.__name__ = func.__name__
        return decorated
    return wrapper


# ==============================
# HOME
# ==============================

@app.route('/')
def home():
    return render_template('index.html')


# ==============================
# LOGIN
# ==============================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        if role == "farmer":
            cursor.execute("SELECT * FROM farmers WHERE email=%s", (email,))
            user = cursor.fetchone()

        elif role == "company":
            cursor.execute("SELECT * FROM companies WHERE email=%s", (email,))
            user = cursor.fetchone()

        elif role == "admin":
            cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
            user = cursor.fetchone()

        else:
            user = None

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = role
            return redirect(f"/{role}/dashboard")

        flash("Invalid credentials")
        return redirect('/login')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ======================================================
# FARMER MODULE
# ======================================================

@app.route('/farmer/register', methods=['GET', 'POST'])
def farmer_register():

    if request.method == 'POST':
        data = request.form
        hashed_password = generate_password_hash(data['password'])

        cursor.execute("""
            INSERT INTO farmers 
            (name,email,phone,address,land_size,crop_type,password)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            data['name'], data['email'], data['phone'],
            data['address'], data['land_size'],
            data['crop_type'], hashed_password
        ))
        db.commit()

        flash("Registration successful")
        return redirect('/login')

    return render_template('Farmer/farmer_register.html')


@app.route('/farmer/dashboard')
@login_required('farmer')
def farmer_dashboard():

    cursor.execute("SELECT * FROM farmers WHERE id=%s", (session['user_id'],))
    farmer = cursor.fetchone()

    return render_template("Farmer/farmer_dashboard.html", farmer=farmer)


@app.route('/farmer/request', methods=['GET', 'POST'])
@login_required('farmer')
def request_fertilizer():

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            INSERT INTO fertilizer_requests
            (farmer_id,crop_type,quantity,harvest_date)
            VALUES (%s,%s,%s,%s)
        """, (session['user_id'], data['crop_type'], data['quantity'], data['harvest_date']))
        db.commit()

    cursor.execute("SELECT * FROM fertilizer_requests WHERE farmer_id=%s", (session['user_id'],))
    requests_data = cursor.fetchall()

    return render_template("Farmer/request_fertilizer.html", requests=requests_data)


@app.route('/farmer/add_waste', methods=['GET', 'POST'])
@login_required('farmer')
def add_waste():

    if request.method == 'POST':
        data = request.form
        image = request.files['image']

        filename = None
        if image and allowed_file(image.filename):
            filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute("""
            INSERT INTO farm_waste
            (farmer_id,waste_type,quantity,price,description,image)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            data['waste_type'],
            data['quantity'],
            data['price'],
            data['description'],
            filename
        ))
        db.commit()

    cursor.execute("SELECT * FROM farm_waste WHERE farmer_id=%s", (session['user_id'],))
    wastes = cursor.fetchall()

    return render_template("Farmer/add_waste.html", wastes=wastes)


@app.route('/farmer/contract', methods=['GET', 'POST'])
@login_required('farmer')
def contract():

    if request.method == 'POST':
        cursor.execute("""
            UPDATE farmers 
            SET contract_status='Accepted', contract_date=%s 
            WHERE id=%s
        """, (datetime.now().date(), session['user_id']))
        db.commit()

    cursor.execute("SELECT contract_status, contract_date FROM farmers WHERE id=%s",
                   (session['user_id'],))
    data = cursor.fetchone()

    return render_template("Farmer/contract_page.html",
                           contract_status=data['contract_status'],
                           contract_date=data['contract_date'])


# ======================================================
# ADMIN MODULE
# ======================================================

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM farmers")
    total_farmers = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM companies")
    total_companies = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM fertilizer_requests")
    total_requests = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM farm_waste")
    total_waste = cursor.fetchone()['total']

    return render_template("Admin/admin_dashboard.html",
                           total_farmers=total_farmers,
                           total_companies=total_companies,
                           total_requests=total_requests,
                           total_waste=total_waste,
                           recent_requests=[],
                           recent_waste=[])


@app.route('/admin/approve')
@login_required('admin')
def approve_requests():

    cursor.execute("""
        SELECT fr.*, f.name AS farmer_name 
        FROM fertilizer_requests fr
        JOIN farmers f ON fr.farmer_id=f.id
    """)
    requests = cursor.fetchall()

    return render_template("Admin/approve_requests.html", requests=requests)


@app.route('/admin/update_request', methods=['POST'])
@login_required('admin')
def update_request():

    request_id = request.form['request_id']
    action = request.form['action']

    status = "Approved" if action == "approve" else "Rejected"

    cursor.execute("UPDATE fertilizer_requests SET status=%s WHERE id=%s",
                   (status, request_id))
    db.commit()

    return redirect('/admin/approve')


@app.route('/admin/manage_waste')
@login_required('admin')
def manage_waste():

    cursor.execute("""
        SELECT fw.*, f.name AS farmer_name
        FROM farm_waste fw
        JOIN farmers f ON fw.farmer_id=f.id
    """)
    wastes = cursor.fetchall()

    return render_template("Admin/manage_waste.html", wastes=wastes)


@app.route('/admin/update_waste', methods=['POST'])
@login_required('admin')
def update_waste():

    waste_id = request.form['waste_id']
    action = request.form['action']

    status = "Approved" if action == "approve" else "Rejected"

    cursor.execute("UPDATE farm_waste SET status=%s WHERE id=%s",
                   (status, waste_id))
    db.commit()

    return redirect('/admin/manage_waste')


@app.route('/admin/reports')
@login_required('admin')
def reports():

    cursor.execute("SELECT COUNT(*) AS total FROM fertilizer_requests")
    total_requests = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM fertilizer_requests WHERE status='Approved'")
    approved_requests = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(quantity) AS total FROM waste_purchases")
    total_waste_sold = cursor.fetchone()['total'] or 0

    cursor.execute("SELECT SUM(total_cost) AS total FROM waste_purchases")
    total_revenue = cursor.fetchone()['total'] or 0

    return render_template("Admin/reports.html",
                           total_requests=total_requests,
                           approved_requests=approved_requests,
                           total_waste_sold=total_waste_sold,
                           total_revenue=total_revenue,
                           monthly_reports=[],
                           waste_reports=[])


# ======================================================
# COMPANY MODULE
# ======================================================

@app.route('/company/dashboard')
@login_required('company')
def company_dashboard():

    return render_template("Company/company_dashboard.html",
                           total_available_waste=0,
                           total_purchased_waste=0,
                           pending_orders=0,
                           total_spent=0,
                           recent_available_waste=[],
                           purchase_history=[])


@app.route('/company/view_waste')
@login_required('company')
def view_waste():

    cursor.execute("""
        SELECT fw.*, f.name AS farmer_name
        FROM farm_waste fw
        JOIN farmers f ON fw.farmer_id=f.id
        WHERE fw.status='Approved'
    """)
    wastes = cursor.fetchall()

    return render_template("Company/view_waste.html", wastes=wastes)


@app.route('/company/purchase_waste')
@login_required('company')
def purchase_waste():

    cursor.execute("""
        SELECT fw.*, f.name AS farmer_name
        FROM farm_waste fw
        JOIN farmers f ON fw.farmer_id=f.id
        WHERE fw.status='Approved'
    """)
    approved_waste = cursor.fetchall()

    cursor.execute("""
        SELECT wp.*, fw.waste_type
        FROM waste_purchases wp
        JOIN farm_waste fw ON wp.waste_id=fw.id
        WHERE wp.company_id=%s
    """, (session['user_id'],))
    purchase_history = cursor.fetchall()

    return render_template("Company/purchase_waste.html",
                           approved_waste=approved_waste,
                           purchase_history=purchase_history)


@app.route('/company/purchase', methods=['POST'])
@login_required('company')
def process_purchase():

    waste_id = request.form['waste_id']
    quantity = int(request.form['purchase_quantity'])

    cursor.execute("SELECT price FROM farm_waste WHERE id=%s", (waste_id,))
    waste = cursor.fetchone()

    total_cost = quantity * float(waste['price'])

    cursor.execute("""
        INSERT INTO waste_purchases
        (waste_id,company_id,quantity,total_cost,status)
        VALUES (%s,%s,%s,%s,'Completed')
    """, (waste_id, session['user_id'], quantity, total_cost))

    db.commit()

    return redirect('/company/purchase_waste')


# ======================================================
# RUN SERVER
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)