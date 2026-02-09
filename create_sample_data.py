#!/usr/bin/env python3
"""
Script to create sample data for SMART Edu Task Manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import User, Class, Subject

def create_sample_data():
    app = create_app()

    with app.app_context():
        # Check if sample data already exists
        sample_class = Class.query.filter_by(name='Sample Class').first()
        if sample_class:
            print("Sample data already exists")
            return

        # Get admin user
        admin = User.query.filter_by(user_type='admin').first()
        if not admin:
            print("Admin user not found. Run create_admin.py first.")
            return

        # Create a subject
        subject = Subject(
            name='Mathematics',
            description='Basic Mathematics',
            created_by=admin.id
        )
        db.session.add(subject)

        # Create a class
        sample_class = Class(
            name='Sample Class',
            description='A sample class for testing',
            created_by=admin.id
        )
        db.session.add(sample_class)
        db.session.commit()  # Commit to get IDs

        # Create a sample student
        student = User(
            name='Sample Student',
            email='student@smartedu.com',
            user_type='student',
            class_id=sample_class.id
        )
        student.set_password('student123')

        # Create a sample teacher
        teacher = User(
            name='Sample Teacher',
            email='teacher@smartedu.com',
            user_type='teacher'
        )
        teacher.set_password('teacher123')

        db.session.add(student)
        db.session.add(teacher)
        db.session.commit()

        # Assign teacher to class
        sample_class.teachers.append(teacher)
        db.session.commit()

        print("Sample data created successfully!")
        print("Student: student@smartedu.com / student123")
        print("Teacher: teacher@smartedu.com / teacher123")
        print("Admin: admin@smartedu.com / admin123")

if __name__ == '__main__':
    create_sample_data()