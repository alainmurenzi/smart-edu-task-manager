#!/usr/bin/env python
"""Script to populate teacher_class_subjects table from existing relationships"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import User, Class, Subject, teacher_class_subjects

def migrate_teacher_class_subjects():
    """Migrate existing teacher-class-subject relationships to teacher_class_subjects table"""
    app = create_app()
    with app.app_context():
        print("Starting migration of teacher_class_subjects...")
        
        # Get all teachers
        teachers = User.query.filter_by(user_type='teacher').all()
        print(f"Found {len(teachers)} teachers")
        
        migrated_count = 0
        for teacher in teachers:
            print(f"\nProcessing teacher: {teacher.name} (ID: {teacher.id})")
            
            # Process each selected subject
            for subject in teacher.selected_subjects:
                print(f"  Subject: {subject.name}")
                
                # For each class the subject is taught in
                for class_obj in subject.classes:
                    print(f"    Class: {class_obj.name}")
                    
                    # Check if entry already exists
                    existing = db.session.query(teacher_class_subjects).filter_by(
                        teacher_id=teacher.id,
                        class_id=class_obj.id,
                        subject_id=subject.id
                    ).first()
                    
                    if existing:
                        print(f"      Entry already exists, skipping")
                    else:
                        # Add the entry
                        db.session.execute(teacher_class_subjects.insert().values(
                            teacher_id=teacher.id,
                            class_id=class_obj.id,
                            subject_id=subject.id
                        ))
                        print(f"      Added entry to teacher_class_subjects")
                        migrated_count += 1
        
        # Also process teaching_classes relationship
        print("\n\nProcessing teaching_classes relationship...")
        for teacher in teachers:
            for class_obj in teacher.teaching_classes:
                # Get subjects the teacher teaches in this class
                for subject in teacher.selected_subjects:
                    if class_obj in subject.classes:
                        existing = db.session.query(teacher_class_subjects).filter_by(
                            teacher_id=teacher.id,
                            class_id=class_obj.id,
                            subject_id=subject.id
                        ).first()
                        
                        if not existing:
                            db.session.execute(teacher_class_subjects.insert().values(
                                teacher_id=teacher.id,
                                class_id=class_obj.id,
                                subject_id=subject.id
                            ))
                            print(f"Added: Teacher {teacher.name} - Class {class_obj.name} - Subject {subject.name}")
                            migrated_count += 1
        
        db.session.commit()
        print(f"\n\nMigration complete! Added {migrated_count} entries to teacher_class_subjects table.")
        
        # Verify
        total_entries = db.session.query(teacher_class_subjects).count()
        print(f"Total entries in teacher_class_subjects: {total_entries}")

if __name__ == '__main__':
    migrate_teacher_class_subjects()
