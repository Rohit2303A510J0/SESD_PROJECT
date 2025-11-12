import psycopg2

DATABASE_URL = "postgresql://travel_admin:g480kuaEIAkc1QIglKw8iPW677wfU89K@dpg-d4a6rqali9vc73fcji30-a.oregon-postgres.render.com/travel_app_2se3"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None
