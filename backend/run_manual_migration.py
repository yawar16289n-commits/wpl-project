from app import create_app, db
from sqlalchemy import text

app = create_app()

def run_migration():
    with app.app_context():
        tables = [
            'users', 'courses', 'course_modules', 'enrollments', 
            'reviews', 'ratings', 'lecture_resources', 'profiles',
            'course_details', 'course_categories', 'progress'
        ]
        
        with db.engine.connect() as conn:
            for table in tables:
                print(f"Checking table {table}...")
                try:
                    # Check if column exists
                    check_query = text(f"SHOW COLUMNS FROM {table} LIKE 'deleted_at'")
                    result = conn.execute(check_query).fetchone()
                    
                    if not result:
                        print(f"Adding deleted_at to {table}...")
                        alter_query = text(f"ALTER TABLE {table} ADD COLUMN deleted_at DATETIME DEFAULT NULL")
                        conn.execute(alter_query)
                        conn.commit()
                        print(f"Successfully added deleted_at to {table}")
                    else:
                        print(f"Column deleted_at already exists in {table}")
                except Exception as e:
                    print(f"Error checking/altering {table}: {e}")
                    
        print("Migration completed.")

if __name__ == "__main__":
    run_migration()
