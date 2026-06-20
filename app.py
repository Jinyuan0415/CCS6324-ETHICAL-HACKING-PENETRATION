import sqlite3
import os
from flask import Flask, request, render_template, redirect, url_for, session

# Get the absolute path to the directory containing app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Force the database to ALWAYS be created/read from inside the web_app folder
DB_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
app.secret_key = 'super_secret_dev_key' # Weak/Hardcoded Secret Key (Bonus Misconfiguration!)

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
		cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
		cursor.execute("INSERT INTO users (username, password, role) VALUES ('student1', 'password123', 'student')")
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
        
		# DANGER: Fulfills OWASP Top 10: SQL Injection via string concatenation
		query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
		
		try:
			cursor.execute(query)
			user = cursor.fetchone()
			conn.close()
		
			if user:
				session['username'] = user[1]
				session['role'] = user[3]
				return redirect(url_for('dashboard'))
			else:
				error = "Invalid credentials."
		except Exception as e:
			error = f"Database Error: {e}"
            
	return render_template('login.html', error=error)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	if 'username' not in session:
		return redirect(url_for('login'))
        
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	
	if request.method == 'POST':
		content = request.form['content']
		# DANGER: Input is saved directly to the database with absolutely no sanitization
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
	# Simple search simulation if a query is provided
	query = request.args.get('q', '')
	all_courses = [
		{"id": 1, "title": "Introduction to Cyber Security", "price": "RM 150"},
		{"id": 2, "title": "Web Application Penetration Testing", "price": "RM 250"},
		{"id": 3, "title": "Network Defense & Countermeasures", "price": "RM 200"}
    	]
	if query:
		filtered_courses = [c for c in all_courses if query.lower() in c['title'].lower()]
	else:
		filtered_courses = all_courses
        
	return render_template('courses.html', courses=filtered_courses, query=query)

@app.route('/payment/<int:course_id>')
def payment(course_id):
    # Mock checkout workflow page
    return render_template('payment.html', course_id=course_id)

if __name__ == '__main__':
	init_db()
	app.run(debug=True, host='0.0.0.0', port=5000)