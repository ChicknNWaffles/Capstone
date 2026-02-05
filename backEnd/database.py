from pathlib import Path
import sqlite3

# This ALWAYS points to the folder where THIS .py file lives
BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "capstone.db"

# Optional: show where it actually is (great for debugging)
print(f"Database location: {DB_FILE}")


def init_db():
    """Create the users table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {Path(DB_FILE).resolve()}")


def add_user(username: str, password: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        print(f"User '{username}' added successfully")
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists")
    finally:
        conn.close()


def fetch_and_verify(username: str, password: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        if result[0] == password:
            print("Authentication successful")
        else:
            print("Incorrect password")
    else:
        print("Username not found")
    
    conn.close()


if __name__ == "__main__":
    # Initialize database & table (safe to run multiple times)
    init_db()

    # Optional: add a test user (uncomment if needed)
    # add_user('testuser', 'pass123')

    # Interactive test
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    fetch_and_verify(username, password)