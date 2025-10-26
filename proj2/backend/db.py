import sqlite3
import os

def init_db():
    # Define the path to the database
    db_path = os.path.join(os.path.dirname(__file__), "requirements.db")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create the table if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS use_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        preconditions TEXT,
        main_flow TEXT,
        sub_flows TEXT,
        alternate_flows TEXT,
        outcomes TEXT,
        stakeholders TEXT
    )
    """)
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
