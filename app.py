from flask import Flask, render_template, request, url_for, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecretkey123'  # Required for session

# Home page
@app.route('/')
def website():
    return render_template('website.html')

# Registration form
@app.route('/register')
def register():
    return render_template('registration.html')

# Submit booking form
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    gender = request.form['gender']
    hobby = request.form['hobby']
    checkin = request.form['checkin']
    checkout = request.form['checkout']

    conn = sqlite3.connect('guesthouse.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, phone TEXT,
        gender TEXT, hobby TEXT, checkin TEXT, checkout TEXT)''')
    c.execute("INSERT INTO bookings (name, email, phone, gender, hobby, checkin, checkout) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (name, email, phone, gender, hobby, checkin, checkout))
    conn.commit()
    conn.close()

    return f"<h2>Thank you, {name}!</h2><p>Email: {email}</p><p>Phone: {phone}</p>"

# ✅ Admin login
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

# ✅ View all bookings (admin only)
@app.route('/view-bookings')
def view_bookings():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('guesthouse.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    data = c.fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=data)

# ✅ Delete booking
@app.route('/delete/<int:id>')
def delete_booking(id):
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('guesthouse.db')
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/view-bookings')

# ✅ Edit booking
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_booking(id):
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('guesthouse.db')
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
                    name = ?, email = ?, phone = ?,
                    gender = ?, hobby = ?, checkin = ?, checkout = ?
                    WHERE id = ?''',
                  (name, email, phone, gender, hobby, checkin, checkout, id))
        conn.commit()
        conn.close()
        return redirect('/view-bookings')

    c.execute("SELECT * FROM bookings WHERE id = ?", (id,))
    booking = c.fetchone()
    conn.close()
    return render_template('edit_booking.html', booking=booking)

# ✅ Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)