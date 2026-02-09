#!/usr/bin/env python
"""Verify teacher_class_subjects data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import User, Class, Subject, teacher_class_subjects

def verify_data():
    app = create_app()
    with app.app_context():
        print("=== teacher_class_subjects table ===")
        entries = db.session.query(teacher_class_subjects).all()
        for e in entries:
            print(f"Teacher ID: {e.teacher_id}, Class ID: {e.class_id}, Subject ID: {e.subject_id}")
        
        print("\n=== Teacher selected_subjects ===")
        teachers = User.query.filter_by(user_type='teacher').all()
        for t in teachers:
            print(f"\nTeacher: {t.name} (ID: {t.id})")
            print(f"  Selected subjects: {[s.name for s in t.selected_subjects]}")
            print(f"  Teaching classes: {[c.name for c in t.teaching_classes]}")
        
        print("\n=== S1A Class subjects ===")
        s1a = Class.query.filter_by(name='S1A').first()
        if s1a:
            print(f"Class: {s1a.name}")
            print(f"Subjects: {[s.name for s in s1a.subjects]}")

if __name__ == '__main__':
    verify_data()
