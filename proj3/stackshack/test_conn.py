import pymysql

# Test connection to MySQL database
try:
    connection = pymysql.connect(
        host="localhost",
        user="root",  # or 'stackshack_user'
        password="root",
        database="stackshack",
    )
    print("✅ Connected to MySQL successfully!")
    connection.close()
except Exception as e:
    print(f"❌ Error: {e}")
