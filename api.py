import os
from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tell Python to go up one level (..), then into the web_app folder
CERT_PATH = os.path.abspath(os.path.join(BASE_DIR, '../web_app/cert.pem'))
KEY_PATH = os.path.abspath(os.path.join(BASE_DIR, '../web_app/key.pem'))

app = Flask(__name__)

# Mock database of student records containing sensitive information
# Subject to PDPA 2010 regulations
STUDENT_RECORDS = {
	"1001": {"name": "Ahmad Bin Razak", "student_id": "243UC246T7", "gpa": "3.85", "phone": "+6012-3456789"},
	"1002": {"name": "Chong Wei Ming", "student_id": "243UC245I9", "gpa": "2.10", "phone": "+6013-9876543"},
	"1003": {"name": "Saraswathy Devi", "student_id": "243UC245E8", "gpa": "3.92", "phone": "+6017-1112233"}
}

# SECURED: Mock database of valid API tokens
# In a real app, these are generated dynamically upon login
VALID_TOKENS = {
    "token_1001": "1001",  # Student 1001's API key
    "token_1002": "1002",  # Student 1002's API key
    "token_admin": "admin" # Admin API key
}

@app.route('/api/v1/students/<student_idx>', methods=['GET'])
def get_student_profile(student_idx):
	# FIX 5.1: BOLA/IDOR Mitigated via API Token Authentication and Authorization
	auth_header = request.headers.get('Authorization')
	
	if not auth_header:
		return jsonify({"error": "Unauthorized. Missing Authorization header."}), 401
		
	# Extract the token (e.g., removing the "Bearer " prefix if present)
	token = auth_header.replace("Bearer ", "")
	user_role_or_id = VALID_TOKENS.get(token)
	
	if not user_role_or_id:
		return jsonify({"error": "Unauthorized. Invalid API token."}), 401
		
	# THE ACTUAL BOLA FIX: Check if they are an admin, OR if they are requesting their OWN data.
	if user_role_or_id != "admin" and user_role_or_id != student_idx:
		return jsonify({"error": "Forbidden. You are not authorized to view this student's record."}), 403
	
	record = STUDENT_RECORDS.get(student_idx)
	if record:
		return jsonify(record), 200
	return jsonify({"error": "Record not found"}), 404

if __name__ == '__main__':
	# Run this component on a completely different port (e.g., 5001) to simulate a multi-tier infrastructure
	app.run(debug=True, host='0.0.0.0', port=5001)