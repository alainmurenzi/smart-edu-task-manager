from app import create_app, db
from models.models import User, Task, Class, Assignment

app = create_app()
with app.app_context():
    # Check teacher Alain
    alain = User.query.filter_by(name='Alain').first()
    if alain:
        print(f'Teacher Alain: id={alain.id}, created_at={alain.created_at}')
    else:
        print('Teacher Alain not found')
    
    # Check student Emmy
    emmy = User.query.filter_by(name='Emmy').first()
    if emmy:
        print(f'Student Emmy: id={emmy.id}, class_id={emmy.class_id}, created_at={emmy.created_at}')
        if emmy.student_class:
            print(f'  Class: {emmy.student_class.name}')
    else:
        print('Student Emmy not found')
    
    # Check class S1A
    s1a = Class.query.filter_by(name='S1A').first()
    if s1a:
        print(f'Class S1A: id={s1a.id}')
    else:
        print('Class S1A not found')
    
    # Check tasks created by Alain
    alain_tasks = Task.query.filter_by(created_by=alain.id).all() if alain else []
    print(f'\nTasks created by Alain ({len(alain_tasks)}):')
    for task in alain_tasks:
        classes = [c.name for c in task.assigned_classes]
        print(f'  Task: {task.title}')
        print(f'    created_at: {task.created_at}')
        print(f'    deadline: {task.deadline}')
        print(f'    assigned_classes: {classes}')
        
    # Check Emmy's assignments
    if emmy:
        assignments = Assignment.query.filter_by(student_id=emmy.id).all()
        print(f'\nEmmy\'s assignments ({len(assignments)}):')
        for a in assignments:
            print(f'  Task: {a.task.title if a.task else "Deleted"}')
            print(f'    status: {a.status}')
