from flask import Flask, request, jsonify
import pyodbc
import os

app = Flask(__name__)

# Connection string do bazy danych Azure SQL
connection_string = os.getenv("DB_CONNECTION_STRING")

# Funkcja do uzyskania połączenia z bazą danych
def get_db_connection():
    return pyodbc.connect(connection_string)

# Endpoint do pobierania listy użytkowników (GET)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Name, Email, Age FROM Users")
    users = cursor.fetchall()
    conn.close()
    users_list = [{"UserID": row[0], "Name": row[1], "Email": row[2], "Age": row[3]} for row in users]
    return jsonify(users_list)

# Endpoint do dodawania użytkownika (POST)
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get("Name")
    email = data.get("Email")
    age = data.get("Age")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (Name, Email, Age) VALUES (?, ?, ?)", (name, email, age))
    conn.commit()
    conn.close()
    return jsonify({"message": "User added successfully"}), 201

# Endpoint do aktualizacji użytkownika (PUT)
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get("Name")
    email = data.get("Email")
    age = data.get("Age")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Name = ?, Email = ?, Age = ? WHERE UserID = ?", (name, email, age, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User updated successfully"}), 200

# Endpoint do usuwania użytkownika (DELETE)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
