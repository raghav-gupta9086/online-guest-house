﻿from flask import Flask, render_template, request, url_for, redirect, session
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="guesthouse"
    )

# Home page
@app.route('/')
def website():
    return render_template('website.html')

# Registration page
@app.route('/register')
def register():
    return render_template('registration.html')

# Handle registration form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    gender = request.form['gender']
    hobby = request.form['hobby']
    checkin = request.form['checkin']
    checkout = request.form['checkout']
    
    # Handle file upload
    file = request.files['file']
    filename = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    else:
        return "Invalid or missing file. Please upload PDF/JPG/PNG only."

    # Insert into DB
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO bookings (name, email, phone, gender, hobby, checkin, checkout, document)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, email, phone, gender, hobby, checkin, checkout, filename))
    conn.commit()
    conn.close()

    return render_template('confirmation.html',
                           name=name,
                           email=email,
                           phone=phone,
                           gender=gender,
                           hobby=hobby,
                           checkin=checkin,
                           checkout=checkout,
                           document=filename)

# Admin login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'Raghav@12345':
            session['admin'] = True
            return redirect('/view-bookings')
        else:
            return "<h3>Invalid credentials</h3><a href='/login'>Try again</a>"

    return render_template('login.html')

# Admin dashboard
@app.route('/view-bookings')
def view_bookings():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    data = c.fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=data)

# Delete a booking
@app.route('/delete/<int:id>')
def delete_booking(id):
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/view-bookings')

# Edit a booking
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_booking(id):
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        hobby = request.form['hobby']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        c.execute('''UPDATE bookings SET
                     name = %s, email = %s, phone = %s,
                     gender = %s, hobby = %s, checkin = %s, checkout = %s
                     WHERE id = %s''',
                  (name, email, phone, gender, hobby, checkin, checkout, id))
        conn.commit()
        conn.close()
        return redirect('/view-bookings')

    c.execute("SELECT * FROM bookings WHERE id = %s", (id,))
    booking = c.fetchone()
    conn.close()
    return render_template('edit_booking.html', booking=booking)

# Admin logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)