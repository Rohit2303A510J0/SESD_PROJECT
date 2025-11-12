import psycopg2

DATABASE_URL = "postgresql://travel_admin:g480kuaEIAkc1QIglKw8iPW677wfU89K@dpg-d4a6rqali9vc73fcji30-a.oregon-postgres.render.com/travel_app_2se3"

def test_database_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT version();")
        result = cur.fetchone()

        cur.close()
        conn.close()

        assert result is not None  # ✅ passes if DB returns version
    except Exception as e:
        assert False, f"❌ Database connection failed: {e}"

