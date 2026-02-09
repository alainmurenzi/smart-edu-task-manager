from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from models.models import User, Task, Assignment, Submission, Notification, Class, Subject, ContactMessage, ChatRoom, ChatMessage
from .forms import AdminUserForm, SystemConfigForm, BulkOperationForm, ClassForm, SubjectForm, AssignTeacherToSubjectForm, TaskForm
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from ml.priority_predictor import predict_priority
import csv
import os

admin = Blueprint('admin', __name__)

@admin.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))

@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    # System statistics
    stats = {
        'total_users': User.query.count(),
        'total_teachers': User.query.filter_by(user_type='teacher').count(),
        'total_students': User.query.filter_by(user_type='student').count(),
        'total_classes': Class.query.count(),
        'total_tasks': Task.query.count(),
        'total_assignments': Assignment.query.count(),
        'total_submissions': Submission.query.count(),
        'completed_assignments': Assignment.query.filter_by(status='completed').count(),
        'overdue_tasks': Task.query.filter(Task.deadline < datetime.utcnow()).count()
    }
    
    # Recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_tasks = Task.query.order_by(desc(Task.created_at)).limit(5).all()
    recent_submissions = Submission.query.order_by(desc(Submission.submitted_at)).limit(5).all()
    
    # Weekly activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_stats = {
        'new_users': User.query.filter(User.created_at >= week_ago).count(),
        'new_tasks': Task.query.filter(Task.created_at >= week_ago).count(),
        'new_submissions': Submission.query.filter(Submission.submitted_at >= week_ago).count()
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_tasks=recent_tasks,
                         recent_submissions=recent_submissions,
                         weekly_stats=weekly_stats)

@admin.route('/users')
@login_required
def manage_users():
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template('admin_users.html', users=users)

@admin.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]
    form.teaching_classes.choices = [(c.id, c.name) for c in Class.query.all()]
    
    # Get subjects from selected classes for teaching_subjects choices
    selected_class_ids = form.teaching_classes.data if form.teaching_classes.data else [c.id for c in user.teaching_classes]
    subjects_in_classes = Subject.query.join(Class.subjects).filter(Class.id.in_(selected_class_ids)).all() if selected_class_ids else []
    form.teaching_subjects.choices = [(s.id, s.name) for s in subjects_in_classes]
    
    # Pre-select current teaching classes and subjects for teachers
    if request.method == 'GET' and user.user_type == 'teacher':
        form.teaching_classes.data = [c.id for c in user.teaching_classes]
        form.teaching_subjects.data = [s.id for s in user.selected_subjects]

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.user_type = form.user_type.data
        user.class_id = form.class_id.data

        # Handle teaching classes for teachers
        if user.user_type == 'teacher':
            user.teaching_classes = []
            for class_id in form.teaching_classes.data:
                class_obj = Class.query.get(class_id)
                if class_obj:
                    user.teaching_classes.append(class_obj)
            
            # Handle teaching subjects for teachers
            user.selected_subjects = []
            for subject_id in form.teaching_subjects.data:
                subject = Subject.query.get(subject_id)
                if subject:
                    user.selected_subjects.append(subject)
            
            # Also populate teacher_class_subjects table for proper tracking
            from models.models import teacher_class_subjects
            # Remove old entries for this teacher
            db.session.query(teacher_class_subjects).filter_by(teacher_id=user.id).delete()
            
            # Add new entries for each class-subject combination
            for class_id in form.teaching_classes.data:
                for subject_id in form.teaching_subjects.data:
                    # Check if the subject belongs to this class
                    class_obj = Class.query.get(class_id)
                    subject = Subject.query.get(subject_id)
                    if class_obj and subject and subject in class_obj.subjects:
                        db.session.execute(teacher_class_subjects.insert().values(
                            teacher_id=user.id,
                            class_id=class_id,
                            subject_id=subject_id
                        ))

        if form.new_password.data:
            user.set_password(form.new_password.data)

        db.session.commit()
        flash(f'User {user.name} updated successfully!')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin_edit_user.html', form=form, user=user)

@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('admin.manage_users'))
    
    # Delete related data first
    # Delete submissions for assignments belonging to this user
    assignment_ids = [assignment.id for assignment in Assignment.query.filter_by(student_id=user.id).all()]
    if assignment_ids:
        Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).delete(synchronize_session=False)
    
    Assignment.query.filter_by(student_id=user.id).delete()
    Task.query.filter_by(created_by=user.id).delete()
    Notification.query.filter_by(user_id=user.id).delete()
    
    # Delete chat messages sent by this user
    ChatMessage.query.filter_by(user_id=user.id).delete()
    
    # Delete chat rooms created by this user
    ChatRoom.query.filter_by(created_by=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} and all related data deleted successfully!')
    return redirect(url_for('admin.manage_users'))

@admin.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = AdminUserForm()
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]
    form.teaching_classes.choices = [(c.id, c.name) for c in Class.query.all()]
    form.teaching_subjects.choices = [(s.id, s.name) for s in Subject.query.all()]

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            user_type=form.user_type.data,
            class_id=form.class_id.data
        )
        user.set_password(form.new_password.data or 'default123')
        
        # Handle teaching classes for teachers
        if user.user_type == 'teacher':
            for class_id in form.teaching_classes.data:
                class_obj = Class.query.get(class_id)
                if class_obj:
                    user.teaching_classes.append(class_obj)
            
            # Handle teaching subjects for teachers
            for subject_id in form.teaching_subjects.data:
                subject = Subject.query.get(subject_id)
                if subject:
                    user.selected_subjects.append(subject)
            
            # Also populate teacher_class_subjects table for proper tracking
            from models.models import teacher_class_subjects
            
            # Add entries for each class-subject combination
            for class_id in form.teaching_classes.data:
                for subject_id in form.teaching_subjects.data:
                    # Check if the subject belongs to this class
                    class_obj = Class.query.get(class_id)
                    subject = Subject.query.get(subject_id)
                    if class_obj and subject and subject in class_obj.subjects:
                        db.session.execute(teacher_class_subjects.insert().values(
                            teacher_id=user.id,
                            class_id=class_id,
                            subject_id=subject_id
                        ))
        
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.name} created successfully!')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin_create_user.html', form=form)

@admin.route('/analytics')
@login_required
def analytics():
    # User analytics
    user_stats = db.session.query(
        User.user_type,
        func.count(User.id).label('count')
    ).group_by(User.user_type).all()
    
    # Task priority distribution
    priority_stats = db.session.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).group_by(Task.priority).all()
    
    # Monthly user registrations (last 12 months)
    monthly_users = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= datetime.utcnow() - timedelta(days=365)).group_by('month').all()
    
    # Assignment status distribution
    assignment_stats = db.session.query(
        Assignment.status,
        func.count(Assignment.id).label('count')
    ).group_by(Assignment.status).all()
    
    return render_template('admin_analytics.html',
                         user_stats=user_stats,
                         priority_stats=priority_stats,
                         monthly_users=monthly_users,
                         assignment_stats=assignment_stats)

@admin.route('/tasks')
@login_required
def manage_tasks():
    tasks = Task.query.join(User, Task.created_by == User.id).add_entity(User).order_by(desc(Task.created_at)).all()
    current_time = datetime.utcnow()
    return render_template('admin_tasks.html', tasks=tasks, current_time=current_time)

@admin.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Delete related data
    # Delete submissions for assignments belonging to this task
    assignment_ids = [assignment.id for assignment in Assignment.query.filter_by(task_id=task.id).all()]
    if assignment_ids:
        Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).delete(synchronize_session=False)
    
    Assignment.query.filter_by(task_id=task.id).delete()
    
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{task.title}" and all related data deleted successfully!')
    return redirect(url_for('admin.manage_tasks'))

@admin.route('/task/<int:task_id>/reassign', methods=['POST'])
@login_required
def reassign_task(task_id):
    """Reassign overdue/completed tasks to newly registered students."""
    task = Task.query.get_or_404(task_id)
    
    # Get already assigned student IDs
    assigned_student_ids = [a.student_id for a in task.assignments]
    
    # Find students registered after the task deadline who are in the assigned classes
    # and don't have an assignment for this task
    new_students = Student.query.join(User).filter(
        User.id.notin_(assigned_student_ids) if assigned_student_ids else True,
        User.created_at > task.deadline
    ).all()
    
    # Also get all students who were not assigned (registered before or after deadline)
    all_students = Student.query.join(User).filter(
        User.id.notin_(assigned_student_ids) if assigned_student_ids else True
    ).all()
    
    # Get the classes this task was assigned to
    assigned_classes = [c.id for c in task.assigned_classes]
    
    assignments_created = 0
    
    for student in all_students:
        # Check if student is in any of the assigned classes
        if student.class_id in assigned_classes:
            # Create new assignment
            assignment = Assignment(
                task_id=task.id,
                student_id=student.id,
                status='pending',
                priority=task.priority
            )
            db.session.add(assignment)
            assignments_created += 1
            
            # Create notification for student
            notification = Notification(
                user_id=student.user_id,
                title='New Task Assignment',
                message=f'You have been assigned a new task: "{task.title}". Deadline: {task.deadline.strftime("%Y-%m-%d %H:%M")}',
                notification_type='task'
            )
            db.session.add(notification)
    
    db.session.commit()
    
    if assignments_created > 0:
        flash(f'Task "{task.title}" has been reassigned to {assignments_created} newly eligible student(s)!')
    else:
        flash(f'No new students found to reassign task "{task.title}".')
    
    return redirect(url_for('admin.manage_tasks'))

@admin.route('/notifications/create', methods=['GET', 'POST'])
@login_required
def create_notification():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        notification_type = request.form.get('notification_type', 'info')
        target_users = request.form.get('target_users', 'all')
        
        # Create system notification
        Notification.create_system_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            target_users=target_users,
            expires_in_hours=168  # 1 week
        )
        
        flash('System notification sent successfully!')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin_create_notification.html')

@admin.route('/export/users')
@login_required
def export_users():
    """Export user data to CSV"""
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'User Type', 'Subject/Class', 'Created At'])
    
    users = User.query.all()
    for user in users:
        writer.writerow([
            user.id,
            user.name,
            user.email,
            user.user_type,
            user.subject or user.class_name or '',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
    )

@admin.route('/classes')
@login_required
def manage_classes():
    classes = Class.query.order_by(desc(Class.created_at)).all()
    return render_template('admin_classes.html', classes=classes)

@admin.route('/subjects')
@login_required
def manage_subjects():
    subjects = Subject.query.order_by(desc(Subject.created_at)).all()
    return render_template('admin_subjects.html', subjects=subjects)

@admin.route('/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    form = SubjectForm()
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(subject)

        # Assign subject to the selected class
        selected_class = Class.query.get(form.class_id.data)
        if selected_class:
            subject.classes.append(selected_class)

        db.session.commit()
        flash(f'Subject "{subject.name}" created and assigned to class "{selected_class.name}" successfully!')
        return redirect(url_for('admin.manage_subjects'))

    return render_template('admin_create_subject.html', form=form)

@admin.route('/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    # Pre-select current class
    if request.method == 'GET' and subject.classes:
        form.class_id.data = subject.classes[0].id

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data

        # Update class assignment
        subject.classes = []
        selected_class = Class.query.get(form.class_id.data)
        if selected_class:
            subject.classes.append(selected_class)

        db.session.commit()
        flash(f'Subject "{subject.name}" updated successfully!')
        return redirect(url_for('admin.manage_subjects'))

    return render_template('admin_edit_subject.html', form=form, subject=subject)

@admin.route('/subject/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    # Check if subject is assigned to any classes
    if subject.classes:
        flash('Cannot delete subject that is assigned to classes.')
        return redirect(url_for('admin.manage_subjects'))

    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{subject.name}" deleted successfully!')
    return redirect(url_for('admin.manage_subjects'))

@admin.route('/class/create', methods=['GET', 'POST'])
@login_required
def create_class():
    form = ClassForm()

    if form.validate_on_submit():
        class_obj = Class(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(class_obj)
        db.session.commit()

        flash(f'Class "{class_obj.name}" created successfully!')
        return redirect(url_for('admin.manage_classes'))

    return render_template('admin_create_class.html', form=form)

@admin.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    form = ClassForm(obj=class_obj)

    if form.validate_on_submit():
        class_obj.name = form.name.data
        class_obj.description = form.description.data
        db.session.commit()
        flash(f'Class "{class_obj.name}" updated successfully!')
        return redirect(url_for('admin.manage_classes'))

    return render_template('admin_edit_class.html', form=form, class_obj=class_obj)

@admin.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Check if class has students or teachers assigned
    if class_obj.students or class_obj.teachers:
        flash('Cannot delete class that has students or teachers assigned.')
        return redirect(url_for('admin.manage_classes'))

    db.session.delete(class_obj)
    db.session.commit()
    flash(f'Class "{class_obj.name}" deleted successfully!')
    return redirect(url_for('admin.manage_classes'))

@admin.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Admin create task and assign to students, classes, teachers, or admins"""
    # Get all classes, students, teachers, and admins
    classes = Class.query.all()
    students = User.query.filter_by(user_type='student').all()
    teachers = User.query.filter_by(user_type='teacher').all()
    admins = User.query.filter_by(user_type='admin').all()
    
    form = TaskForm()
    form.assigned_classes.choices = [(str(c.id), c.name) for c in classes]
    form.assigned_students.choices = [(s.id, f"{s.name} ({s.student_class.name if s.student_class else 'No class'})") for s in students]
    form.assigned_teacher_id.choices = [(0, '-- No specific teacher --')] + [(t.id, t.name) for t in teachers]
    suggested_priority = None
    
    if form.validate_on_submit():
        # Use ML to suggest priority if not set
        suggested_priority = predict_priority(form.description.data)
        if not form.priority.data:
            form.priority.data = suggested_priority

        # Handle file upload
        file_path = None
        if form.task_file.data:
            filename = secure_filename(form.task_file.data.filename)
            if filename:
                # Create unique filename
                import uuid
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                form.task_file.data.save(file_path)

        # Get assigned teacher ID (None if 0)
        assigned_teacher_id = form.assigned_teacher_id.data if form.assigned_teacher_id.data != 0 else None
        
        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            priority=form.priority.data,
            instructions=form.instructions.data,
            file_path=file_path,
            created_by=current_user.id,
            assigned_teacher_id=assigned_teacher_id
        )
        db.session.add(task)
        db.session.commit()

        # Add assigned classes to the task
        if form.assigned_classes.data:
            for class_id in form.assigned_classes.data:
                class_obj = Class.query.get(int(class_id))
                if class_obj:
                    task.assigned_classes.append(class_obj)
            db.session.commit()

        # Create assignments for students
        assigned_students = []
        
        # First, assign to specific students if selected
        if form.assigned_students.data:
            for student_id in form.assigned_students.data:
                student = User.query.get(int(student_id))
                if student:
                    existing = Assignment.query.filter_by(task_id=task.id, student_id=student.id).first()
                    if not existing:
                        assignment = Assignment(
                            task_id=task.id,
                            student_id=student.id
                        )
                        db.session.add(assignment)
                        assigned_students.append(student.id)
        
        # Then, assign to students in selected classes (if no specific students selected)
        if not form.assigned_students.data and form.assigned_classes.data:
            for class_id in form.assigned_classes.data:
                class_obj = Class.query.get(int(class_id))
                if class_obj:
                    for student in class_obj.students:
                        existing = Assignment.query.filter_by(task_id=task.id, student_id=student.id).first()
                        if not existing:
                            assignment = Assignment(
                                task_id=task.id,
                                student_id=student.id
                            )
                            db.session.add(assignment)
                            assigned_students.append(student.id)
        
        db.session.commit()

        # Create notifications for assigned students
        for student_id in assigned_students:
            student = User.query.get(student_id)
            if student:
                notification = Notification(
                    user_id=student_id,
                    title="New Task Assigned",
                    message=f"Task '{task.title}' has been assigned by {current_user.name}",
                    notification_type='info'
                )
                db.session.add(notification)
        
        # Notify the assigned teacher
        if assigned_teacher_id:
            teacher = User.query.get(assigned_teacher_id)
            if teacher:
                notification = Notification(
                    user_id=teacher.id,
                    title='Task Assigned to You',
                    message=f'A task "{task.title}" has been assigned to you by admin {current_user.name}.',
                    notification_type='task'
                )
                db.session.add(notification)
        
        # Notify selected teachers (for class notification)
        notify_teachers = request.form.getlist('notify_teachers')
        for teacher_id in notify_teachers:
            teacher = User.query.get(int(teacher_id))
            if teacher:
                notification = Notification(
                    user_id=teacher.id,
                    title='Task Assigned to Class',
                    message=f'A task "{task.title}" has been assigned by admin {current_user.name}.',
                    notification_type='task'
                )
                db.session.add(notification)
        
        # Notify selected admins
        notify_admins = request.form.getlist('notify_admins')
        for admin_id in notify_admins:
            admin = User.query.get(int(admin_id))
            if admin:
                notification = Notification(
                    user_id=admin.id,
                    title='Task Created',
                    message=f'A new task "{task.title}" has been created by admin {current_user.name}.',
                    notification_type='task'
                )
                db.session.add(notification)
        
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('admin.manage_tasks'))

    # Get suggestion for display
    if form.description.data:
        suggested_priority = predict_priority(form.description.data)

    return render_template('admin_create_task.html', form=form, suggested_priority=suggested_priority,
                          classes=classes, students=students, teachers=teachers, admins=admins)

@admin.route('/task/<int:task_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_task_to_users(task_id):
    """Admin assign existing task to specific students, classes, teachers, or admins"""
    task = Task.query.get_or_404(task_id)
    
    # Get all users
    students = User.query.filter_by(user_type='student').all()
    teachers = User.query.filter_by(user_type='teacher').all()
    admins = User.query.filter_by(user_type='admin').all()
    classes = Class.query.all()
    
    if request.method == 'POST':
        assign_students = request.form.getlist('assign_students')
        assign_classes = request.form.getlist('assign_classes')
        assign_teachers = request.form.getlist('assign_teachers')
        assign_admins = request.form.getlist('assign_admins')
        
        assigned_count = 0
        
        # Assign to specific students
        for student_id in assign_students:
            student = User.query.get(int(student_id))
            if student:
                existing = Assignment.query.filter_by(task_id=task.id, student_id=student.id).first()
                if not existing:
                    assignment = Assignment(
                        task_id=task.id,
                        student_id=student.id
                    )
                    db.session.add(assignment)
                    assigned_count += 1
                    
                    # Create notification
                    notification = Notification(
                        user_id=student.id,
                        title="New Task Assigned",
                        message=f"Task '{task.title}' has been assigned by {current_user.name}",
                        notification_type='info'
                    )
                    db.session.add(notification)
        
        # Assign to students in classes
        for class_id in assign_classes:
            class_obj = Class.query.get(int(class_id))
            if class_obj:
                # Add class to task's assigned classes
                if class_obj not in task.assigned_classes:
                    task.assigned_classes.append(class_obj)
                
                for student in class_obj.students:
                    existing = Assignment.query.filter_by(task_id=task.id, student_id=student.id).first()
                    if not existing:
                        assignment = Assignment(
                            task_id=task.id,
                            student_id=student.id
                        )
                        db.session.add(assignment)
                        assigned_count += 1
                        
                        # Create notification
                        notification = Notification(
                            user_id=student.id,
                            title="New Task Assigned",
                            message=f"Task '{task.title}' has been assigned by {current_user.name}",
                            notification_type='info'
                        )
                        db.session.add(notification)
        
        # Note: Teachers and admins don't have assignments, but we can send them notifications
        for teacher_id in assign_teachers:
            teacher = User.query.get(int(teacher_id))
            if teacher:
                notification = Notification(
                    user_id=teacher.id,
                    title='Task Assigned to Class',
                    message=f'A task "{task.title}" has been assigned to a class you teach.',
                    notification_type='task'
                )
                db.session.add(notification)
        
        for admin_id in assign_admins:
            admin = User.query.get(int(admin_id))
            if admin:
                notification = Notification(
                    user_id=admin.id,
                    title='Task Assigned',
                    message=f'A task "{task.title}" has been assigned by admin {current_user.name}.',
                    notification_type='task'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        flash(f'Task "{task.title}" assigned to {assigned_count} student(s)!', 'success')
        return redirect(url_for('admin.manage_tasks'))
    
    # Get already assigned students
    assigned_student_ids = [a.student_id for a in task.assignments]
    
    return render_template('admin_assign_task.html', task=task, students=students, 
                          teachers=teachers, admins=admins, classes=classes,
                          assigned_student_ids=assigned_student_ids)

@admin.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = {
        'total_users': User.query.count(),
        'total_teachers': User.query.filter_by(user_type='teacher').count(),
        'total_students': User.query.filter_by(user_type='student').count(),
        'total_classes': Class.query.count(),
        'total_tasks': Task.query.count(),
        'completed_assignments': Assignment.query.filter_by(status='completed').count()
    }
    return jsonify(stats)

@admin.route('/class/<int:class_id>/subjects')
@login_required
def manage_class_subjects(class_id):
    """View all subjects in a class and manage teacher assignments"""
    class_obj = Class.query.get_or_404(class_id)
    subjects = class_obj.subjects
    teachers = User.query.filter_by(user_type='teacher').all()
    
    # Create a form for each subject to assign teachers
    forms = {}
    for subject in subjects:
        form = AssignTeacherToSubjectForm()
        # Get teachers who are NOT already assigned to this subject in this class
        assigned_teacher_ids = [t.id for t in subject.teaching_teachers if class_obj in t.teaching_classes]
        available_teachers = [(t.id, t.name) for t in teachers if t.id not in assigned_teacher_ids]
        form.teacher_id.choices = [(0, '-- Select Teacher --')] + available_teachers
        forms[subject.id] = form
    
    return render_template('admin_class_subjects.html', 
                         class_obj=class_obj, 
                         subjects=subjects, 
                         teachers=teachers,
                         forms=forms)

# Contact Message Management Routes
@admin.route('/contact-messages')
@login_required
def view_contact_messages():
    """View all contact messages with filtering options"""
    filter_param = request.args.get('filter', 'all')
    
    # Build query based on filter
    if filter_param == 'unread':
        messages = ContactMessage.query.filter_by(is_read=False).order_by(desc(ContactMessage.created_at)).all()
    elif filter_param in ['general', 'support', 'bug', 'feature', 'partnership']:
        messages = ContactMessage.query.filter_by(category=filter_param).order_by(desc(ContactMessage.created_at)).all()
    else:
        messages = ContactMessage.query.order_by(desc(ContactMessage.created_at)).all()
    
    # Calculate statistics
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    general_count = ContactMessage.query.filter_by(category='general').count()
    support_count = ContactMessage.query.filter_by(category='support').count()
    
    return render_template('admin_contact_messages.html', 
                         messages=messages, 
                         filter=filter_param,
                         unread_count=unread_count,
                         general_count=general_count,
                         support_count=support_count)

@admin.route('/contact-message/<int:message_id>/read')
@login_required
def mark_contact_message_read(message_id):
    """Mark a contact message as read"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    flash(f'Message from {message.name} marked as read.', 'success')
    return redirect(url_for('admin.view_contact_messages'))

@admin.route('/contact-message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_contact_message(message_id):
    """Delete a contact message"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash(f'Message from {message.name} deleted successfully.', 'success')
    return redirect(url_for('admin.view_contact_messages'))
    # Create a form for each subject to assign teachers
    forms = {}
    for subject in subjects:
        form = AssignTeacherToSubjectForm()
        # Get teachers who are NOT already assigned to this subject in this class
        assigned_teacher_ids = [t.id for t in subject.teaching_teachers if class_obj in t.teaching_classes]
        available_teachers = [(t.id, t.name) for t in teachers if t.id not in assigned_teacher_ids]
        form.teacher_id.choices = [(0, '-- Select Teacher --')] + available_teachers
        forms[subject.id] = form
    
    return render_template('admin_class_subjects.html', 
                         class_obj=class_obj, 
                         subjects=subjects, 
                         teachers=teachers,
                         forms=forms)

@admin.route('/class/<int:class_id>/subject/<int:subject_id>/assign-teacher', methods=['POST'])
@login_required
def assign_teacher_to_subject(class_id, subject_id):
    """Assign a teacher to a subject in a specific class"""
    class_obj = Class.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    
    form = AssignTeacherToSubjectForm()
    teachers = User.query.filter_by(user_type='teacher').all()
    assigned_teacher_ids = [t.id for t in subject.teaching_teachers if class_obj in t.teaching_classes]
    available_teachers = [(t.id, t.name) for t in teachers if t.id not in assigned_teacher_ids]
    form.teacher_id.choices = [(0, '-- Select Teacher --')] + available_teachers
    
    if form.validate_on_submit():
        teacher_id = form.teacher_id.data
        if teacher_id == 0:
            flash('Please select a teacher.', 'warning')
            return redirect(url_for('admin.manage_class_subjects', class_id=class_id))
        
        teacher = User.query.get_or_404(teacher_id)
        
        # Add teacher to subject's teaching teachers
        if teacher not in subject.teaching_teachers:
            subject.teaching_teachers.append(teacher)
        
        # Add class to teacher's teaching classes if not already there
        if class_obj not in teacher.teaching_classes:
            teacher.teaching_classes.append(class_obj)
        
        # Add subject to teacher's selected subjects if not already there
        if subject not in teacher.selected_subjects:
            teacher.selected_subjects.append(subject)
        
        # Add entry to teacher_class_subjects table for proper tracking
        from models.models import teacher_class_subjects
        existing_entry = db.session.query(teacher_class_subjects).filter_by(
            teacher_id=teacher.id, class_id=class_obj.id, subject_id=subject.id
        ).first()
        if not existing_entry:
            db.session.execute(teacher_class_subjects.insert().values(
                teacher_id=teacher.id, class_id=class_obj.id, subject_id=subject.id
            ))
        
        db.session.commit()
        flash(f'Teacher "{teacher.name}" has been assigned to subject "{subject.name}" in class "{class_obj.name}".', 'success')
    else:
        flash('Error assigning teacher. Please try again.', 'danger')
    
    return redirect(url_for('admin.manage_class_subjects', class_id=class_id))

@admin.route('/class/<int:class_id>/subject/<int:subject_id>/remove-teacher/<int:teacher_id>', methods=['POST'])
@login_required
def remove_teacher_from_subject(class_id, subject_id, teacher_id):
    """Remove a teacher from a subject in a specific class"""
    class_obj = Class.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    teacher = User.query.get_or_404(teacher_id)
    
    # Remove the relationship
    if teacher in subject.teaching_teachers:
        subject.teaching_teachers.remove(teacher)
    
    # Check if teacher still teaches any subjects in this class
    teacher_subjects_in_class = [s for s in teacher.selected_subjects if class_obj in s.classes]
    if not teacher_subjects_in_class:
        # Remove class from teacher's teaching classes if no more subjects
        if class_obj in teacher.teaching_classes:
            teacher.teaching_classes.remove(class_obj)
    
    db.session.commit()
    flash(f'Teacher "{teacher.name}" has been removed from subject "{subject.name}".', 'success')
    return redirect(url_for('admin.manage_class_subjects', class_id=class_id))