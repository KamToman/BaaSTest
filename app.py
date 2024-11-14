from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:mybassserver.database.windows.net,1433;Database=MyBaaSDb;Uid=BaaS;Pwd=!Haslo123123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    conn = pyodbc.connect(connection_string)
    return conn

# Endpoint to get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()
    user_list = [{"UserID": row.UserID, "Name": row.Name, "Email": row.Email, "Age": row.Age} for row in users]
    return jsonify(user_list)

# Endpoint to add a new user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    age = data.get("age")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (Name, Email, Age) VALUES (?, ?, ?)", (name, email, age))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User added successfully"}), 201

# Endpoint to get a single user by UserID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_data = {"UserID": user.UserID, "Name": user.Name, "Email": user.Email, "Age": user.Age}
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

# Endpoint to update a user by UserID
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    age = data.get("age")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Name = ?, Email = ?, Age = ? WHERE UserID = ?", (name, email, age, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User updated successfully"})

# Endpoint to delete a user by UserID
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
