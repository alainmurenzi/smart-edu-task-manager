"""Script to create forum tables in the database"""
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import ChatRoom, ChatMessage

def create_forum_tables():
    """Create forum tables"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Forum tables created successfully!")
        
        # Create teacher forum if it doesn't exist
        teacher_room = ChatRoom.query.filter_by(room_type='teacher').first()
        if not teacher_room:
            teacher_room = ChatRoom(
                name="Teachers Forum",
                room_type='teacher',
                class_id=None,
                created_by=1
            )
            db.session.add(teacher_room)
            db.session.commit()
            print("Created Teachers Forum room!")
        else:
            print("Teachers Forum already exists!")

if __name__ == '__main__':
    create_forum_tables()
