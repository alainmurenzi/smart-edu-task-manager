from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.models import Assignment, Task, User, Class, Subject, teacher_class_subjects
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Gather statistics for homepage
    from models.models import User, Task, Assignment, Submission
    
    # Get user counts
    total_teachers = User.query.filter_by(user_type='teacher').count()
    total_students = User.query.filter_by(user_type='student').count()
    total_users = total_teachers + total_students
    
    # Get task and assignment statistics
    total_tasks = Task.query.count()
    total_assignments = Assignment.query.count()
    
    # Calculate completion statistics
    completed_assignments = Assignment.query.filter_by(status='completed').count()
    completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
    
    # Get overdue assignments
    overdue_assignments = Assignment.query.filter(
        Assignment.status != 'completed'
    ).join(Assignment.task).filter(
        Task.deadline < datetime.utcnow()
    ).count()
    
    # Get recent submissions (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_submissions = Submission.query.filter(
        Submission.submitted_at >= week_ago
    ).count()
    
    # Get active tasks (tasks with future deadlines)
    active_tasks = Task.query.filter(
        Task.deadline >= datetime.utcnow()
    ).count()
    
    stats = {
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_tasks': total_tasks,
        'total_assignments': total_assignments,
        'completion_rate': round(completion_rate, 1),
        'overdue_assignments': overdue_assignments,
        'recent_submissions': recent_submissions,
        'active_tasks': active_tasks
    }
    
    return render_template('index.html', stats=stats)

@main.route('/test_auth')
def test_auth():
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.name} ({current_user.user_type})"
    else:
        return "Not logged in"

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contacts', methods=['GET', 'POST'])
def contacts():
    from .forms import ContactForm
    from models.models import ContactMessage
    
    form = ContactForm()
    if form.validate_on_submit():
        # Save the contact message to the database
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
            category=form.subject.data
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Your message has been sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('main.contacts'))
    
    return render_template('contacts.html', form=form)

@main.route('/faqs')
def faqs():
    return render_template('faqs.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    if current_user.user_type == 'teacher':
        # Render teacher dashboard with classes and subjects
        tasks = Task.query.filter_by(created_by=current_user.id).all()
        
        # Get teacher's classes from teacher_class_subjects table
        teacher_classes = []
        class_subject_mapping = db.session.query(teacher_class_subjects).filter_by(teacher_id=current_user.id).all()
        for tc in class_subject_mapping:
            class_obj = Class.query.get(tc.class_id)
            if class_obj and class_obj not in teacher_classes:
                teacher_classes.append(class_obj)
        
        # Also get from teaching_classes relationship (backwards compatibility)
        for class_obj in current_user.teaching_classes:
            if class_obj not in teacher_classes:
                teacher_classes.append(class_obj)
        
        students = []
        for class_obj in teacher_classes:
            students.extend(class_obj.students)
        students = list(set(students))

        student_stats = []
        for student in students:
            assignments = Assignment.query.filter_by(student_id=student.id).all()
            assignments = [a for a in assignments if a.task is not None]
            total_tasks = len(assignments)
            completed_tasks = len([a for a in assignments if a.status == 'completed'])
            in_progress_tasks = len([a for a in assignments if a.status == 'in_progress'])
            overdue_tasks = len([a for a in assignments if a.is_overdue])

            student_stats.append({
                'student': student,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            })
        
        # Get teacher's classes with subject information
        teacher_classes_info = []
        for class_obj in teacher_classes:
            available_subjects = class_obj.subjects
            teaching_subjects = []
            for subject in available_subjects:
                entry = db.session.query(teacher_class_subjects).filter_by(
                    teacher_id=current_user.id, 
                    class_id=class_obj.id, 
                    subject_id=subject.id
                ).first()
                if entry:
                    teaching_subjects.append(subject)
            
            selected_subject_ids = [s.id for s in current_user.selected_subjects]
            for subject in available_subjects:
                if subject.id in selected_subject_ids and subject not in teaching_subjects:
                    teaching_subjects.append(subject)

            teacher_classes_info.append({
                'class': class_obj,
                'available_subjects': available_subjects,
                'teaching_subjects': teaching_subjects,
                'student_count': len(class_obj.students)
            })
        
        return render_template('teacher_dashboard.html', tasks=tasks, student_stats=student_stats, teacher_classes_info=teacher_classes_info)
    
    if current_user.user_type == 'student':
        # Check for overdue assignments and update status
        overdue_assignments = Assignment.query.filter_by(
            student_id=current_user.id,
            status='pending'
        ).join(Assignment.task).filter(
            Assignment.task.has(datetime.utcnow() > Task.deadline)
        ).all()

        if overdue_assignments:
            for assignment in overdue_assignments:
                assignment.status = 'overdue'
            db.session.commit()
            flash(f'You have {len(overdue_assignments)} overdue assignment(s)!', 'warning')
        
        # Render student dashboard
        assignments = Assignment.query.filter_by(student_id=current_user.id).all()
        # Filter out assignments with deleted tasks
        assignments = [a for a in assignments if a.task is not None]
        # Sort by priority and deadline
        priority_order = {
            'urgent_important': 1,
            'important_not_urgent': 2,
            'urgent_not_important': 3,
            'high_priority': 4,
            'medium_priority': 5,
            'low_priority': 6,
            'long_term': 7,
            'group_task': 8,
            'optional': 9,
            'not_important_not_urgent': 10
        }
        assignments.sort(key=lambda x: (priority_order.get(x.task.priority, 99), x.task.deadline))
        return render_template('student_dashboard.html', assignments=assignments)
    
    if current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    flash('Invalid user type. Please contact administrator.')
    return redirect(url_for('main.index'))
