"""
Migration script to add assigned_teacher_id column to Task table.
"""
from app import db
from models.models import Task

def migrate():
    # Add the column if it doesn't exist
    try:
        # Try to add the column using raw SQL
        db.session.execute(db.text("""
            ALTER TABLE task ADD COLUMN assigned_teacher_id INTEGER REFERENCES user(id)
        """))
        db.session.commit()
        print("Column 'assigned_teacher_id' added successfully!")
    except Exception as e:
        # If column already exists, this will fail - that's OK
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("Column 'assigned_teacher_id' already exists - skipping migration")
        else:
            print(f"Error adding column: {e}")
            # Try a different approach - check if column exists first
            try:
                result = db.session.execute(db.text("""
                    SELECT assigned_teacher_id FROM task LIMIT 1
                """))
                print("Column 'assigned_teacher_id' already exists")
            except:
                print("Could not verify column existence")
        db.session.rollback()

if __name__ == '__main__':
    migrate()
