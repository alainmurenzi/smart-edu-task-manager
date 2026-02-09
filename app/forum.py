from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.models import ChatRoom, ChatMessage, User, Class
from datetime import datetime, timedelta

forum = Blueprint('forum', __name__)


def get_class_members(class_id):
    """Get all members (students and teachers) of a class with their activity status"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return [], []
    
    # Get students in the class
    students = User.query.filter_by(class_id=class_id, user_type='student').all()
    
    # Get teachers teaching this class
    teachers = list(class_obj.teachers)
    
    # Determine active status (active if logged in within last 5 minutes)
    active_time = datetime.utcnow() - timedelta(minutes=5)
    
    for student in students:
        student.is_active_forum = student.created_at >= active_time
    
    for teacher in teachers:
        teacher.is_active_forum = teacher.created_at >= active_time
    
    return students, teachers


def get_teacher_forum_members():
    """Get all teachers with their activity status"""
    teachers = User.query.filter_by(user_type='teacher').all()
    
    # Determine active status
    active_time = datetime.utcnow() - timedelta(minutes=5)
    
    for teacher in teachers:
        teacher.is_active_forum = teacher.created_at >= active_time
    
    return teachers

# ============================================
# STUDENT FORUM ROUTES
# ============================================

@forum.route('/forum/class/<int:class_id>')
@login_required
def class_forum(class_id):
    """Student class forum - only students from the same class can access"""
    # Get the class
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if user is a student in this class
    if current_user.user_type == 'student':
        if current_user.class_id != class_id:
            flash('You can only access your own class forum.', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.user_type == 'teacher':
        # Teachers can access class forums for classes they teach
        teacher_classes = db.session.query(Class).join(
            'teachers'
        ).filter(User.id == current_user.id).all()
        if class_obj not in teacher_classes and class_obj not in current_user.teaching_classes:
            flash('You can only access forums for classes you teach.', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.user_type != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get or create the chat room
    room = ChatRoom.get_or_create_class_room(class_id, current_user.id)
    
    # Get messages (most recent first)
    messages = ChatMessage.query.filter_by(
        room_id=room.id, 
        is_deleted=False
    ).order_by(ChatMessage.created_at.desc()).limit(100).all()
    messages = list(reversed(messages))
    
    # Get class members
    students, teachers = get_class_members(class_id)
    
    return render_template(
        'forum_class.html', 
        class_obj=class_obj, 
        room=room, 
        messages=messages,
        students=students,
        teachers=teachers
    )


@forum.route('/forum/class/<int:class_id>/post', methods=['POST'])
@login_required
def post_class_message(class_id):
    """Post a message to the class forum"""
    # Get the class
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if user can post
    if current_user.user_type == 'student':
        if current_user.class_id != class_id:
            flash('You can only post in your own class forum.', 'danger')
            return redirect(url_for('forum.class_forum', class_id=class_id))
    elif current_user.user_type == 'teacher':
        teacher_classes = db.session.query(Class).join(
            'teachers'
        ).filter(User.id == current_user.id).all()
        if class_obj not in teacher_classes and class_obj not in current_user.teaching_classes:
            flash('You can only post in forums for classes you teach.', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.user_type != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get or create the chat room
    room = ChatRoom.get_or_create_class_room(class_id, current_user.id)
    
    # Get message content
    content = request.form.get('content', '').strip()
    if not content:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('forum.class_forum', class_id=class_id))
    
    # Create the message
    message = ChatMessage(
        room_id=room.id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Message posted successfully!', 'success')
    return redirect(url_for('forum.class_forum', class_id=class_id))


# ============================================
# TEACHER FORUM ROUTES
# ============================================

@forum.route('/forum/teachers')
@login_required
def teachers_forum():
    """Teacher institution-wide forum - only teachers and admins can access"""
    if current_user.user_type not in ['teacher', 'admin']:
        flash('Access denied. Only teachers can access this forum.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get or create the teacher chat room
    room = ChatRoom.get_or_create_teacher_room(current_user.id)
    
    # Get messages (most recent first)
    messages = ChatMessage.query.filter_by(
        room_id=room.id, 
        is_deleted=False
    ).order_by(ChatMessage.created_at.desc()).limit(100).all()
    messages = list(reversed(messages))
    
    # Get all teachers
    teachers = get_teacher_forum_members()
    
    return render_template(
        'forum_teachers.html', 
        room=room, 
        messages=messages,
        teachers=teachers
    )


@forum.route('/forum/teachers/post', methods=['POST'])
@login_required
def post_teacher_message():
    """Post a message to the teachers forum"""
    if current_user.user_type not in ['teacher', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get or create the teacher chat room
    room = ChatRoom.get_or_create_teacher_room(current_user.id)
    
    # Get message content
    content = request.form.get('content', '').strip()
    if not content:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('forum.teachers_forum'))
    
    # Create the message
    message = ChatMessage(
        room_id=room.id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Message posted successfully!', 'success')
    return redirect(url_for('forum.teachers_forum'))


# ============================================
# ADMIN FORUM MANAGEMENT ROUTES
# ============================================

@forum.route('/admin/forums')
@login_required
def admin_forums():
    """Admin view - list all forums and their messages"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all chat rooms
    class_rooms = ChatRoom.query.filter_by(room_type='class').all()
    teacher_room = ChatRoom.query.filter_by(room_type='teacher').first()
    
    return render_template(
        'admin_forums.html',
        class_rooms=class_rooms,
        teacher_room=teacher_room
    )


@forum.route('/admin/forum/<int:room_id>')
@login_required
def admin_view_forum(room_id):
    """Admin view - view all messages in a specific forum"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    room = ChatRoom.query.get_or_404(room_id)
    messages = ChatMessage.query.filter_by(
        room_id=room.id,
        is_deleted=False
    ).order_by(ChatMessage.created_at.desc()).all()
    messages = list(reversed(messages))
    
    return render_template(
        'admin_view_forum.html',
        room=room,
        messages=messages
    )


@forum.route('/admin/forum/message/<int:message_id>/delete', methods=['POST'])
@login_required
def admin_delete_message(message_id):
    """Admin - delete a message"""
    if current_user.user_type != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    message = ChatMessage.query.get_or_404(message_id)
    message.is_deleted = True
    db.session.commit()
    
    flash('Message deleted.', 'success')
    return redirect(url_for('forum.admin_view_forum', room_id=message.room_id))


# ============================================
# STUDENT'S MY CLASS FORUM (from dashboard)
# ============================================

@forum.route('/my-class-forum')
@login_required
def my_class_forum():
    """Direct access to student's class forum from dashboard"""
    if current_user.user_type != 'student' or not current_user.class_id:
        flash('You are not assigned to a class.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return redirect(url_for('forum.class_forum', class_id=current_user.class_id))


# ============================================
# API ROUTES FOR REAL-TIME UPDATES
# ============================================

@forum.route('/api/forum/<int:room_id>/messages')
@login_required
def api_get_messages(room_id):
    """API endpoint to get messages for a room (for potential real-time updates)"""
    room = ChatRoom.query.get_or_404(room_id)
    
    # Check access
    if room.room_type == 'class':
        class_obj = room.class_group
        if current_user.user_type == 'student':
            if current_user.class_id != class_obj.id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user.user_type == 'teacher':
            teacher_classes = db.session.query(Class).join(
                'teachers'
            ).filter(User.id == current_user.id).all()
            if class_obj not in teacher_classes and class_obj not in current_user.teaching_classes:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user.user_type != 'admin':
            return jsonify({'error': 'Access denied'}), 403
    elif room.room_type == 'teacher':
        if current_user.user_type not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
    
    # Get messages
    last_id = request.args.get('last_id', 0, type=int)
    messages = ChatMessage.query.filter(
        ChatMessage.room_id == room.id,
        ChatMessage.is_deleted == False,
        ChatMessage.id > last_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return jsonify([{
        'id': m.id,
        'user_id': m.user_id,
        'user_name': m.user.name,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages])


# ============================================
# MESSAGE EDIT/DELETE ROUTES
# ============================================

def get_room_and_verify_access(message_id):
    """Helper to get message and verify user has access"""
    message = ChatMessage.query.get_or_404(message_id)
    room = message.room
    
    if room.room_type == 'class':
        class_obj = room.class_group
        if current_user.user_type == 'student':
            if current_user.class_id != class_obj.id:
                return None, None, False
        elif current_user.user_type == 'teacher':
            teacher_classes = db.session.query(Class).join(
                'teachers'
            ).filter(User.id == current_user.id).all()
            if class_obj not in teacher_classes and class_obj not in current_user.teaching_classes:
                return None, None, False
        elif current_user.user_type != 'admin':
            return None, None, False
    elif room.room_type == 'teacher':
        if current_user.user_type not in ['teacher', 'admin']:
            return None, None, False
    
    # Check if user owns the message or is admin
    if message.user_id != current_user.id and current_user.user_type != 'admin':
        return None, None, False
    
    return message, room, True


@forum.route('/forum/message/<int:message_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    """Edit a message - only by the message owner or admin"""
    message, room, has_access = get_room_and_verify_access(message_id)
    
    if not has_access:
        flash('You do not have permission to edit this message.', 'danger')
        if room:
            if room.room_type == 'class':
                return redirect(url_for('forum.class_forum', class_id=room.class_id))
            else:
                return redirect(url_for('forum.teachers_forum'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('Message cannot be empty.', 'danger')
        else:
            message.content = content
            db.session.commit()
            flash('Message updated successfully!', 'success')
            
            if room.room_type == 'class':
                return redirect(url_for('forum.class_forum', class_id=room.class_id))
            else:
                return redirect(url_for('forum.teachers_forum'))
    
    return render_template('forum_edit_message.html', message=message, room=room)


@forum.route('/forum/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a message - only by the message owner or admin"""
    message, room, has_access = get_room_and_verify_access(message_id)
    
    if not has_access:
        flash('You do not have permission to delete this message.', 'danger')
        if room:
            if room.room_type == 'class':
                return redirect(url_for('forum.class_forum', class_id=room.class_id))
            else:
                return redirect(url_for('forum.teachers_forum'))
        return redirect(url_for('main.dashboard'))
    
    # Soft delete the message
    message.is_deleted = True
    db.session.commit()
    
    flash('Message deleted.', 'success')
    
    if room.room_type == 'class':
        return redirect(url_for('forum.class_forum', class_id=room.class_id))
    else:
        return redirect(url_for('forum.teachers_forum'))
