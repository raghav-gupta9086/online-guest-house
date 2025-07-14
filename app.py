from flask import Flask, render_template, request, url_for, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mysecretkey123'  

# 🔗 Function to get MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="guesthouse"
    )


@app.route('/')
def website():
    return render_template('website.html')


@app.route('/register')
def register():
    return render_template('registration.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    gender = request.form['gender']
    hobby = request.form['hobby']
    checkin = request.form['checkin']
    checkout = request.form['checkout']

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO bookings (name, email, phone, gender, hobby, checkin, checkout) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (name, email, phone, gender, hobby, checkin, checkout))
    conn.commit()
    conn.close()

    return f"""
    <h2>Thank you, {name}!</h2>
    <p>Email: {email}</p>
    <p>Phone: {phone}</p>
    <br>
    <a href="/" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Back to Home</a>
    &nbsp;
    <a href="/register" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">New Booking</a>
    """

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

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)