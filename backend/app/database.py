import os
import psycopg2

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        print("DATABASE_URL not set in environment!")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None
