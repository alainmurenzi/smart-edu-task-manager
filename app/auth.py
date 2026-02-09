from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
from app import db
from models.models import User, Class, Task, Assignment, Notification, task_classes
from .forms import LoginForm, TeacherRegistrationForm, StudentRegistrationForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = TeacherRegistrationForm()

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, user_type='teacher')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered teacher!')
        return redirect(url_for('auth.login'))

    return render_template('register_teacher.html', title='Register as Teacher', form=form)

@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = StudentRegistrationForm()
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, user_type='student',
                    class_id=form.class_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Auto-assign tasks to the new student based on class assignments
        student_class_id = form.class_id.data
        
        # Find all tasks assigned to this class (using the assigned_classes relationship)
        tasks = Task.query.join(task_classes).filter(
            task_classes.c.class_id == student_class_id
        ).all()
        
        # Create assignments for tasks not already assigned to this student
        for task in tasks:
            existing = Assignment.query.filter_by(task_id=task.id, student_id=user.id).first()
            if not existing:
                assignment = Assignment(
                    task_id=task.id,
                    student_id=user.id,
                    status='pending'
                )
                db.session.add(assignment)
                
                # Create notification
                notification = Notification(
                    user_id=user.id,
                    title='New Task Assignment',
                    message=f'You have been assigned a new task: "{task.title}". Deadline: {task.deadline.strftime("%Y-%m-%d %H:%M")}',
                    notification_type='task'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        flash('Congratulations, you are now a registered student!')
        return redirect(url_for('auth.login'))

    return render_template('register_student.html', title='Register as Student', form=form)