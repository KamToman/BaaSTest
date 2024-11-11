from flask import Flask, request, jsonify
from urllib.parse import quote as url_quote
import pyodbc
import os

app = Flask(__name__)

# Retrieve and quote the connection string to avoid issues with special characters
connection_string = os.getenv("DB_CONNECTION_STRING")
if connection_string:
    connection_string = url_quote(connection_string)
else:
    raise ValueError("DB_CONNECTION_STRING environment variable is not set.")

# Function to establish a connection with the database
def get_db_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Endpoint to get the list of users (GET)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Name, Email, Age FROM Users")
        users = cursor.fetchall()
        users_list = [{"UserID": row[0], "Name": row[1], "Email": row[2], "Age": row[3]} for row in users]
        return jsonify(users_list)
    finally:
        conn.close()

# Endpoint to add a user (POST)
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get("Name")
    email = data.get("Email")
    age = data.get("Age")

    # Check for required fields
    if not all([name, email, age]):
        return jsonify({"error": "Missing required fields: Name, Email, or Age"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (Name, Email, Age) VALUES (?, ?, ?)", (name, email, age))
        conn.commit()
        return jsonify({"message": "User added successfully"}), 201
    finally:
        conn.close()

# Endpoint to update a user (PUT)
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get("Name")
    email = data.get("Email")
    age = data.get("Age")

    # Check for required fields
    if not all([name, email, age]):
        return jsonify({"error": "Missing required fields: Name, Email, or Age"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Name = ?, Email = ?, Age = ? WHERE UserID = ?", (name, email, age, user_id))
        conn.commit()
        return jsonify({"message": "User updated successfully"}), 200
    finally:
        conn.close()

# Endpoint to delete a user (DELETE)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection error"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
        conn.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
