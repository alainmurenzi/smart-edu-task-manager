from app import create_app, db
from models.models import User, Class, Task, Assignment

app = create_app()
ctx = app.app_context()
ctx.push()

# Get student Emmy
student = User.query.filter_by(name='Emmy').first()
if not student:
    print("Student 'Emmy' not found!")
    ctx.pop()
    exit()

print(f"Student: {student.name}")
print(f"Student class: {student.student_class.name if student.student_class else 'None'}")

# Get all tasks assigned to the student's class
if student.student_class:
    tasks = Task.query.join(Task.assigned_classes).filter(
        Class.id == student.student_class.id
    ).all()
    print(f"\nTasks assigned to {student.student_class.name}:")
    for task in tasks:
        print(f"  - {task.title} (ID: {task.id})")
        
        # Check if assignment exists
        existing = Assignment.query.filter_by(task_id=task.id, student_id=student.id).first()
        if existing:
            print(f"    Already assigned!")
        else:
            # Create assignment
            assignment = Assignment(
                task_id=task.id,
                student_id=student.id,
                status='pending'
            )
            db.session.add(assignment)
            print(f"    Assignment created!")
    
    db.session.commit()
    print("\nCommit successful!")
else:
    print("Student has no class assigned!")

ctx.pop()
