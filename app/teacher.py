from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app import db
from models.models import Task, Assignment, User, Submission, Class, Subject, teacher_class_subjects
from .forms import TaskForm, AssignmentForm, TeacherSubjectForm
from ml.priority_predictor import predict_priority
from datetime import datetime
import os
from werkzeug.utils import secure_filename

teacher = Blueprint('teacher', __name__)

@teacher.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    # Get tasks created by this teacher
    tasks = Task.query.filter_by(created_by=current_user.id).all()
    
    # Get tasks assigned to this teacher by admin
    assigned_tasks = Task.query.filter_by(assigned_teacher_id=current_user.id).all()
    
    # Combine both lists
    all_tasks = list(tasks) + list(assigned_tasks)
    
    # Remove duplicates based on task ID
    unique_tasks = {}
    for task in all_tasks:
        if task.id not in unique_tasks:
            unique_tasks[task.id] = task
    tasks = list(unique_tasks.values())

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
    # Remove duplicates in case a student is in multiple classes
    students = list(set(students))

    student_stats = []
    for student in students:
        assignments = Assignment.query.filter_by(student_id=student.id).all()
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
        # Get subjects available in this class
        available_subjects = class_obj.subjects
        # Get subjects the teacher is assigned to teach in this class (from teacher_class_subjects table)
        teaching_subjects = []
        for subject in available_subjects:
            # Check if there's an entry in teacher_class_subjects for this teacher, class, and subject
            entry = db.session.query(teacher_class_subjects).filter_by(
                teacher_id=current_user.id, 
                class_id=class_obj.id, 
                subject_id=subject.id
            ).first()
            if entry:
                teaching_subjects.append(subject)
        
        # Also include subjects from selected_subjects (for backwards compatibility)
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
    
    print(f"DEBUG: Teacher {current_user.name} has {len(teacher_classes_info)} classes")
    
    return render_template('teacher_dashboard.html',
                         tasks=tasks,
                         student_stats=student_stats,
                         teacher_classes_info=teacher_classes_info)

@teacher.route('/select_subjects', methods=['GET', 'POST'])
@login_required
def select_subjects():
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    form = TeacherSubjectForm()

    # Get all subjects from the teacher's classes
    teacher_classes = current_user.teaching_classes
    available_subjects = []
    for class_obj in teacher_classes:
        for subject in class_obj.subjects:
            available_subjects.append((subject.id, f"{subject.name} ({class_obj.name})"))

    form.subjects.choices = available_subjects

    if request.method == 'GET':
        # Pre-select currently selected subjects
        current_selected_ids = [subject.id for subject in current_user.selected_subjects]
        form.subjects.data = current_selected_ids

    if form.validate_on_submit():
        # Clear existing subject selections
        current_user.selected_subjects.clear()

        # Add selected subjects
        selected_subjects = []
        for subject_id in form.subjects.data:
            subject = Subject.query.get(int(subject_id))
            if subject:
                selected_subjects.append(subject)

        current_user.selected_subjects.extend(selected_subjects)
        db.session.commit()

        selected_count = len(form.subjects.data)
        flash(f'Successfully updated your teaching subjects! You now teach {selected_count} subject(s).')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher_select_subjects.html', form=form, teacher_classes=teacher_classes)

@teacher.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    # Get classes that the teacher teaches
    teacher_classes = []
    
    # First, check teacher_class_subjects table (new way)
    class_subject_mapping = db.session.query(teacher_class_subjects).filter_by(teacher_id=current_user.id).all()
    for tc in class_subject_mapping:
        class_obj = Class.query.get(tc.class_id)
        if class_obj and class_obj not in teacher_classes:
            teacher_classes.append(class_obj)
    
    # Also check teaching_classes relationship (backwards compatibility)
    for class_obj in current_user.teaching_classes:
        if class_obj not in teacher_classes:
            teacher_classes.append(class_obj)
    
    # Get all students from teacher's classes
    students = []
    for class_obj in teacher_classes:
        students.extend(class_obj.students)
    students = list(set(students))

    form = TaskForm()
    form.assigned_classes.choices = [(c.id, c.name) for c in teacher_classes]
    form.assigned_students.choices = [(s.id, f"{s.name} ({s.student_class.name if s.student_class else 'No class'})") for s in students]
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

        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            priority=form.priority.data,
            instructions=form.instructions.data,
            file_path=file_path,
            created_by=current_user.id
        )
        db.session.add(task)
        db.session.commit()

        # Add assigned classes to the task (for tracking which classes the task is assigned to)
        if form.assigned_classes.data:
            for class_id in form.assigned_classes.data:
                class_obj = Class.query.get(int(class_id))
                if class_obj and class_obj not in task.assigned_classes:
                    task.assigned_classes.append(class_obj)
            db.session.commit()

        # Create assignments for students
        assigned_students = []
        
        # First, assign to specific students if selected
        if form.assigned_students.data:
            for student_id in form.assigned_students.data:
                student = User.query.get(int(student_id))
                if student:
                    # Check if assignment already exists
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
                        # Check if assignment already exists
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
        from app.notifications import notify_task_assigned
        for student_id in assigned_students:
            student = User.query.get(student_id)
            if student:
                notify_task_assigned(student_id, task.title, current_user.name)

        flash('Task created successfully!', 'success')
        return redirect(url_for('teacher.dashboard'))
    else:
        # Form validation failed - show errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')

    # Get suggestion for display
    if form.description.data:
        suggested_priority = predict_priority(form.description.data)

    return render_template('create_task.html', form=form, suggested_priority=suggested_priority)

@teacher.route('/assign_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def assign_task(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))
    
    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))
    
    # Get students from the teacher's classes only
    teacher_classes = current_user.teaching_classes
    students = []
    for class_obj in teacher_classes:
        students.extend(class_obj.students)
    # Remove duplicates in case a student is in multiple classes
    students = list(set(students))

    form = AssignmentForm()
    form.students.choices = [(str(s.id), s.name) for s in students]
    
    if form.validate_on_submit():
        selected_students = request.form.getlist('students')
        assigned_students = []
        for student_id in selected_students:
            assignment = Assignment(task_id=task.id, student_id=int(student_id))
            db.session.add(assignment)
            assigned_students.append(int(student_id))
        db.session.commit()
        
        # Create notifications for assigned students
        from app.notifications import notify_task_assigned
        for student_id in assigned_students:
            student = User.query.get(student_id)
            if student:
                notify_task_assigned(student_id, task.title, current_user.name)
        
        flash('Task assigned successfully!')
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('assign_task.html', form=form, task=task)

@teacher.route('/task_progress/<int:task_id>')
@login_required
def task_progress(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))

    assignments = Assignment.query.filter_by(task_id=task_id).all()
    return render_template('task_progress.html', task=task, assignments=assignments)

@teacher.route('/view_submission/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def view_submission(assignment_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))

    submission = Submission.query.filter_by(assignment_id=assignment_id).first()
    
    # Handle feedback submission
    if request.method == 'POST':
        score = request.form.get('score')
        feedback = request.form.get('feedback')
        
        if score:
            try:
                score_int = int(score)
                if 0 <= score_int <= 100:
                    if submission:
                        # Update existing submission with feedback
                        submission.score = score_int
                        submission.feedback = feedback
                        submission.feedback_provided_at = datetime.utcnow()
                        submission.graded_by = current_user.id
                    else:
                        # Create new submission with feedback (edge case)
                        submission = Submission(
                            assignment_id=assignment_id,
                            score=score_int,
                            feedback=feedback,
                            feedback_provided_at=datetime.utcnow(),
                            graded_by=current_user.id
                        )
                        db.session.add(submission)
                    
                    db.session.commit()
                    
                    # Create notification for student
                    from app.notifications import notify_feedback_received
                    notify_feedback_received(assignment.student_id, assignment.task.title, score_int)
                    
                    flash('Feedback provided successfully!')
                else:
                    flash('Score must be between 0 and 100')
            except ValueError:
                flash('Invalid score format')
        else:
            flash('Score is required')
        
        return redirect(url_for('teacher.view_submission', assignment_id=assignment_id))
    
    return render_template('view_submission.html', assignment=assignment, submission=submission)

@teacher.route('/download_file/<int:submission_id>')
@login_required
def download_file(submission_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))

    if not submission.file_path or not os.path.exists(submission.file_path):
        flash('File not found')
        return redirect(url_for('teacher.view_submission', assignment_id=submission.assignment_id))

    return send_file(submission.file_path, as_attachment=True)

@teacher.route('/download_task_file/<int:task_id>')
@login_required
def download_task_file(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))

    if not task.file_path or not os.path.exists(task.file_path):
        flash('File not found')
        return redirect(url_for('teacher.dashboard'))

    return send_file(task.file_path, as_attachment=True)

@teacher.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))

    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))

    # Get classes that the teacher teaches
    teacher_classes = current_user.teaching_classes

    form = TaskForm()
    form.assigned_classes.choices = [(str(c.id), c.name) for c in teacher_classes]

    # Populate form with existing task data
    if request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.deadline.data = task.deadline
        form.priority.data = task.priority
        form.instructions.data = task.instructions

        # Pre-select assigned classes (find classes that have students assigned to this task)
        current_assignments = Assignment.query.filter_by(task_id=task.id).all()
        assigned_class_ids = set()
        for assignment in current_assignments:
            if assignment.student.class_id:
                assigned_class_ids.add(assignment.student.class_id)
        form.assigned_classes.data = list(assigned_class_ids)

    if form.validate_on_submit():
        # Use ML to suggest priority if not set or changed
        suggested_priority = predict_priority(form.description.data)
        if not form.priority.data or form.priority.data != task.priority:
            form.priority.data = suggested_priority

        # Handle file upload
        file_path = task.file_path  # Keep existing file by default
        if form.task_file.data:
            filename = secure_filename(form.task_file.data.filename)
            if filename:
                # Remove old file if exists
                if task.file_path and os.path.exists(task.file_path):
                    os.remove(task.file_path)

                # Create unique filename
                import uuid
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                form.task_file.data.save(file_path)

        # Update task
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.priority = form.priority.data
        task.instructions = form.instructions.data
        task.file_path = file_path

        # Update assignments
        if form.assigned_classes.data:
            # Remove existing assignments
            Assignment.query.filter_by(task_id=task.id).delete()
            db.session.commit()

            # Create new assignments for students in selected classes
            assigned_students = []
            for class_id in form.assigned_classes.data:
                class_obj = Class.query.get(int(class_id))
                if class_obj:
                    for student in class_obj.students:
                        assignment = Assignment(
                            task_id=task.id,
                            student_id=student.id
                        )
                        db.session.add(assignment)
                        assigned_students.append(student.id)

            db.session.commit()

            # Create notifications for newly assigned students
            from app.notifications import notify_task_assigned, notify_task_updated
            for student_id in assigned_students:
                student = User.query.get(student_id)
                if student:
                    notify_task_assigned(student_id, task.title, current_user.name)
        else:
            # If no classes selected, remove all assignments and send update notification
            assigned_students = []
            for assignment in Assignment.query.filter_by(task_id=task.id).all():
                assigned_students.append(assignment.student_id)

            # Create notifications for students whose task was updated
            from app.notifications import notify_task_updated
            if assigned_students:
                notify_task_updated(assigned_students, task.title, current_user.name)
        flash('Task updated successfully!')
        return redirect(url_for('teacher.dashboard'))

    # Get suggestion for display
    if form.description.data:
        suggested_priority = predict_priority(form.description.data)

    return render_template('edit_task.html', form=form, task=task, suggested_priority=suggested_priority)

@teacher.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))
    
    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))
    
    try:
        # Remove associated file if exists
        if task.file_path and os.path.exists(task.file_path):
            os.remove(task.file_path)
        
        # Delete all related assignments and submissions
        assignments = Assignment.query.filter_by(task_id=task.id).all()
        for assignment in assignments:
            # Remove submission files
            submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
            for submission in submissions:
                if submission.file_path and os.path.exists(submission.file_path):
                    os.remove(submission.file_path)
                db.session.delete(submission)
            db.session.delete(assignment)
        
        # Delete the task
        db.session.delete(task)
        db.session.commit()
        flash('Task and all related data deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}')
    
    return redirect(url_for('teacher.dashboard'))

@teacher.route('/review_submissions/<int:task_id>')
@login_required
def review_submissions(task_id):
    if current_user.user_type != 'teacher':
        return redirect(url_for('main.dashboard'))
    
    task = Task.query.get_or_404(task_id)
    if task.created_by != current_user.id:
        flash('Access denied')
        return redirect(url_for('teacher.dashboard'))
    
    assignments = Assignment.query.filter_by(task_id=task_id).all()
    
    # Get submission data for each assignment
    submissions_data = []
    for assignment in assignments:
        submission = Submission.query.filter_by(assignment_id=assignment.id).first()
        submissions_data.append({
            'assignment': assignment,
            'submission': submission,
            'student': assignment.student
        })
    
    return render_template('review_submissions.html', task=task, submissions_data=submissions_data)
