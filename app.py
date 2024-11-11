from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Connection string to Azure SQL Database
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=tcp:mydbserver-baas.database.windows.net,1433;"
    "Database=MyBaaSDb;"
    "Uid=baas;"
    "Pwd=!Haslo123123;"
)

# Pydantic model for the user
class User(BaseModel):
    Name: str
    Email: str
    Age: int

class UserInDB(User):
    UserID: int

# Utility function to get database connection
def get_db_connection():
    return pyodbc.connect(connection_string)

# Endpoint to get all users (GET)
@app.get("/api/users", response_model=List[UserInDB])
async def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Name, Email, Age FROM Users")
    rows = cursor.fetchall()
    conn.close()
    users = [{"UserID": row[0], "Name": row[1], "Email": row[2], "Age": row[3]} for row in rows]
    return users

# Endpoint to add a new user (POST)
@app.post("/api/users", response_model=UserInDB)
async def add_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (Name, Email, Age) OUTPUT INSERTED.UserID VALUES (?, ?, ?)", 
                   (user.Name, user.Email, user.Age))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {**user.dict(), "UserID": user_id}

# Endpoint to update a user (PUT)
@app.put("/api/users/{user_id}", response_model=UserInDB)
async def update_user(user_id: int, user: User):
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

# Endpoint to delete a user (DELETE)
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}
