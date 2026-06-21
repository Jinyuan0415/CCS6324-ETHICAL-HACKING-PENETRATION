import sqlite3
import os
import html
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, session

# Get the absolute path to the directory containing app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Force the database to ALWAYS be created/read from inside the web_app folder
DB_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)

# FIX 5.3 (Crypto): Generated a cryptographically strong, random 256-bit secret key
app.secret_key = secrets.token_hex(32)

AVAILABLE_COURSES = [
    {"id": 1, "title": "Introduction to Cyber Security", "price": "RM 150"},
    {"id": 2, "title": "Web Application Penetration Testing", "price": "RM 250"},
    {"id": 3, "title": "Network Defense & Countermeasures", "price": "RM 200"}
]

def init_db():
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	# Fulfills Cryptographic Weakness: Storing plain text passwords
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			password TEXT NOT NULL,
			role TEXT NOT NULL
		)
	''')

	# 2. Announcements Table (For Stored XSS)
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS announcements (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		author TEXT NOT NULL,
		content TEXT NOT NULL
		)
	''')
    
	# Seed Data
	cursor.execute("SELECT * FROM users WHERE username='admin'")
	if not cursor.fetchone():
		# FIX 5.3 (Crypto): Passwords are now hashed using PBKDF2:sha256 before storing
		admin_hash = generate_password_hash('admin123')
		student_hash = generate_password_hash('password123')

		cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', admin_hash, 'admin'))
		cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('student1', student_hash, 'student'))
		cursor.execute("INSERT INTO announcements (author, content) VALUES ('System', 'Welcome to MyEduConnect! Keep your passwords safe.')")
		conn.commit()
	conn.close()

@app.route('/')
def index():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
        
		conn = sqlite3.connect(DB_PATH)
		cursor = conn.cursor()
        
		# FIX 5.1: SQL Injection mitigated using parameterized queries.
		# Note: We only query the username now, because we must verify the password hash in Python.
		query = "SELECT * FROM users WHERE username = ?"
		
		try:
			cursor.execute(query, (username,))
			user = cursor.fetchone()
			conn.close()

			# FIX 5.3 (Crypto): Safely compare the provided password against the stored hash
			if user and check_password_hash(user[2], password):
				session['username'] = user[1]
				session['role'] = user[3]
				return redirect(url_for('dashboard'))
			else:
				error = "Invalid credentials."
		except Exception as e:
			error = f"Database Error: {e}"
            
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        
        # SECURE: Hash the password immediately upon registration
        hashed_password = generate_password_hash(raw_password)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, 'student'))
            conn.commit()
        except sqlite3.Error:
            pass # In a real app, handle duplicate usernames here
        finally:
            conn.close()
            
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'], role=session.get('role'))

@app.route('/admin')
def admin_panel():
	# 1. If not logged in at all, redirect to login page
    if 'username' not in session:
        return redirect(url_for('login'))
        
    # 2. If logged in, but NOT an admin, show the error
    if session.get('role') != 'admin':
        return "Error: Unauthorized Access. Admins only.", 403
        
    # 3. If both pass, load the admin panel
    return render_template('admin.html', username=session['username'])

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	if 'username' not in session:
		return redirect(url_for('login'))
        
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	
	if request.method == 'POST':
		# FIX 5.1: Stored XSS mitigated by encoding HTML entities before database insertion
		content = html.escape(request.form['content'])
		cursor.execute("INSERT INTO announcements (author, content) VALUES (?, ?)", (session['username'], content))
		conn.commit()
        
	cursor.execute("SELECT author, content FROM announcements ORDER BY id DESC")
	all_announcements = cursor.fetchall()
	conn.close()
	
	return render_template('dashboard.html', username=session['username'], announcements=all_announcements)

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

@app.route('/courses')
def courses():
	# # FIX 5.1: Broken Access Control mitigated by enforcing session validation
	if 'username' not in session:
		return redirect(url_for('login'))

	# Simple search simulation if a query is provided
	query = request.args.get('q', '')

	if query:
		filtered_courses = [c for c in AVAILABLE_COURSES if query.lower() in c['title'].lower()]
	else:
		filtered_courses = AVAILABLE_COURSES
        
	return render_template('courses.html', courses=filtered_courses, query=query)

@app.route('/payment/<int:course_id>')
def payment(course_id):
	# FIX 5.1: Broken Object Level Authorization (BOLA/IDOR) mitigated via session checks
	if 'username' not in session:
		return redirect(url_for('login'))
	
	# Python dynamically checks if the course_id matches any ID in our global list
	course_exists = any(course['id'] == course_id for course in AVAILABLE_COURSES)
    
	if not course_exists:
		return "Error: Course does not exist or unauthorized access.", 403

	# YOU WERE MISSING THIS LINE:
	return render_template('payment.html', course_id=course_id)

if __name__ == '__main__':
	init_db()

	CERT_PATH = os.path.join(BASE_DIR, 'cert.pem')
	KEY_PATH = os.path.join(BASE_DIR, 'key.pem')

	app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=(CERT_PATH, KEY_PATH))