from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pyodbc
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Connection string to Azure SQL Database
connection_string = (Server=tcp:mybassserver.database.windows.net,1433;Initial Catalog=MyBaaSDb;Persist Security Info=False;User ID=
wrx81713@student.wroclaw.merito.pl;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Authentication="Active Directory Integrated";)

# Pydantic model for the user
class User(BaseModel):
    Name: str
    Email: str
    Age: int

class UserInDB(User):
    UserID: int

# Utility function to get database connection
def get_db_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# Home endpoint
@app.get("/")
async def home():
    return {"message": "Hello"}

# Endpoint to get all users (GET)
@app.get("/api/users", response_model=List[UserInDB])
async def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Name, Email, Age FROM Users")
        rows = cursor.fetchall()
        conn.close()

        users = [{"UserID": row[0], "Name": row[1], "Email": row[2], "Age": row[3]} for row in rows]
        return users

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")

# Endpoint to add a new user (POST)
@app.post("/api/users", response_model=UserInDB)
async def add_user(user: User):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Users (Name, Email, Age) OUTPUT INSERTED.UserID VALUES (?, ?, ?)", 
            (user.Name, user.Email, user.Age)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return {**user.dict(), "UserID": user_id}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error inserting user: {e}")

# Endpoint to update a user (PUT)
@app.put("/api/users/{user_id}", response_model=UserInDB)
async def update_user(user_id: int, user: User):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Users SET Name = ?, Email = ?, Age = ? WHERE UserID = ?", 
            (user.Name, user.Email, user.Age, user_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        conn.close()

        return {**user.dict(), "UserID": user_id}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")

# Endpoint to delete a user (DELETE)
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        conn.close()

        return {"message": "User deleted successfully"}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
