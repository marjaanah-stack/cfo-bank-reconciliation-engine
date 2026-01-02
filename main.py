import os
from sqlalchemy import create_engine

# 1. Get the secret we just saved
db_url = os.environ.get('DATABASE_URL')

def test_connection():
    try:
        # 2. Try to connect to the database
        engine = create_engine(db_url)
        connection = engine.connect()
        print("🚀 CONNECTION SUCCESSFUL!")
        print("Replit is now officially talking to Supabase.")
        connection.close()
    except Exception as e:
        print("❌ CONNECTION FAILED")
        print(f"Error details: {e}")
        print("\nCommon fixes:")
        print("- Check if you removed the [brackets] from your password.")
        print("- Ensure the secret name is exactly 'DATABASE_URL' in all caps.")

if __name__ == "__main__":
    test_connection()