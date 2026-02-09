from app import create_app, db
from models.models import User, Class, Task, Assignment, task_classes

app = create_app()
ctx = app.app_context()
ctx.push()

# Check all tasks and their assigned classes
print("=== All tasks with their assigned classes ===")
tasks = Task.query.all()
for task in tasks:
    print(f"\nTask: {task.title}")
    print(f"  ID: {task.id}")
    print(f"  Created at: {task.created_at}")
    print(f"  Deadline: {task.deadline}")
    print(f"  Assigned classes: {[c.name for c in task.assigned_classes]}")

# Check task_classes table directly
print("\n=== Direct query of task_classes table ===")
from sqlalchemy import select
result = db.session.execute(select(task_classes))
for row in result:
    print(f"  Task ID: {row.task_id}, Class ID: {row.class_id}")

# Check student Emmy
print("\n=== Student info ===")
student = User.query.filter_by(name='Emmy').first()
if student:
    print(f"Student: {student.name}")
    print(f"  ID: {student.id}")
    print(f"  Class: {student.student_class.name if student.student_class else 'None'}")
    print(f"  Created at: {student.created_at}")

    # Check assignments for this student
    print(f"\n  Assignments:")
    assignments = Assignment.query.filter_by(student_id=student.id).all()
    for a in assignments:
        print(f"    - Task ID: {a.task_id}, Status: {a.status}")

    # Check if task "fgggf" should be assigned
    task = Task.query.filter_by(title='fgggf').first()
    if task:
        print(f"\n  Task 'fgggf':")
        print(f"    ID: {task.id}")
        print(f"    Deadline: {task.deadline}")
        print(f"    UTC now: {db.func.utc_timestamp()}")
        from datetime import datetime
        print(f"    Python utcnow: {datetime.utcnow()}")
        print(f"    Is deadline in future: {task.deadline > datetime.utcnow()}")

        # Check if class matches
        task_class_ids = [c.id for c in task.assigned_classes]
        student_class_id = student.student_class.id if student.student_class else None
        print(f"    Task class IDs: {task_class_ids}")
        print(f"    Student class ID: {student_class_id}")
        print(f"    Student class in task classes: {student_class_id in task_class_ids}")

ctx.pop()
