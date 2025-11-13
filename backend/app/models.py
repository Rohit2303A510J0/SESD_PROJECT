from app.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Favorites table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        attraction_id INTEGER REFERENCES attractions(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Attractions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attractions (
        id SERIAL PRIMARY KEY,
        country VARCHAR(100) NOT NULL,
        name VARCHAR(200) NOT NULL,
        lat FLOAT NOT NULL,
        lng FLOAT NOT NULL,
        description TEXT,
        image1 TEXT,
        image2 TEXT,
        image3 TEXT,
        image4 TEXT,
        status VARCHAR(50) DEFAULT 'available'
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created (if they didn't exist)")
