from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models.models import User, Class, Subject

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    class Meta:
        csrf = False

class TeacherRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as Teacher')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    class Meta:
        csrf = False

class StudentRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    class_id = SelectField('Class', choices=[], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Register as Student')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    class Meta:
        csrf = False

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Task Description', validators=[DataRequired()])
    deadline = DateTimeField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('urgent_important', 'Urgent & Important'),
        ('important_not_urgent', 'Important but Not Urgent'),
        ('urgent_not_important', 'Urgent but Not Important'),
        ('not_important_not_urgent', 'Not Important & Not Urgent'),
        ('high_priority', 'High Priority (High Marks / Major Assignment)'),
        ('medium_priority', 'Medium Priority'),
        ('low_priority', 'Low Priority'),
        ('optional', 'Optional / Extra Work'),
        ('long_term', 'Long-term Project'),
        ('group_task', 'Group Task')
    ], validators=[DataRequired()])
    instructions = TextAreaField('Additional Instructions')
    task_file = FileField('Attach File (Optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'ppt', 'pptx', 'xls', 'xlsx'],
                    'Only document, presentation, and image files allowed!'),
        FileSize(max_size=20*1024*1024, message='File size must be less than 20MB!')
    ])
    assigned_classes = SelectMultipleField('Assign to Classes', choices=[], validators=[], coerce=int)
    assigned_students = SelectMultipleField('Assign to Specific Students (Optional)', choices=[], validators=[], coerce=int)
    assigned_teacher_id = SelectField('Assign to Teacher (Optional - for Admin)', choices=[('', 'None')], coerce=lambda x: int(x) if x else None)
    submit = SubmitField('Create Task')

class AssignmentForm(FlaskForm):
    students = SelectField('Assign to Students', choices=[], validators=[DataRequired()])
    submit = SubmitField('Assign Task')

class SubmissionForm(FlaskForm):
    content = TextAreaField('Submission Content')
    file = FileField('Upload File (optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'], 'Only document and image files allowed!'),
        FileSize(max_size=10*1024*1024, message='File size must be less than 10MB!')
    ])
    submit = SubmitField('Submit Work')

class AdminUserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('User Type', choices=[
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('student', 'Student')
    ], validators=[DataRequired()])
    class_id = SelectField('Class (for Students)', choices=[], coerce=int)
    teaching_classes = SelectMultipleField('Classes to Teach (for Teachers)', choices=[], validators=[], coerce=int)
    teaching_subjects = SelectMultipleField('Subjects to Teach (for Teachers)', choices=[], validators=[], coerce=int)
    new_password = PasswordField('New Password (leave empty to keep current)')
    new_password2 = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update User')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.id != getattr(self, 'user_id', None):
            raise ValidationError('Please use a different email address.')

class SystemConfigForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description', validators=[Length(max=500)])
    allow_registration = BooleanField('Allow User Registration')
    require_email_verification = BooleanField('Require Email Verification')
    max_file_size = StringField('Max File Upload Size (MB)', validators=[DataRequired()])
    session_timeout = StringField('Session Timeout (minutes)', validators=[DataRequired()])
    submit = SubmitField('Update Settings')

class BulkOperationForm(FlaskForm):
    operation = SelectField('Operation', choices=[
        ('delete_users', 'Delete Selected Users'),
        ('send_notification', 'Send Notification to Users'),
        ('export_data', 'Export Selected User Data')
    ], validators=[DataRequired()])
    target_users = SelectField('Target Users', choices=[
        ('all', 'All Users'),
        ('teachers', 'Teachers Only'),
        ('students', 'Students Only'),
        ('selected', 'Selected Users')
    ], validators=[DataRequired()])
    submit = SubmitField('Execute Operation')
    submit = SubmitField('Submit Work')

class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    class_id = SelectField('Class', choices=[], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Create Subject')

    def validate_name(self, name):
        # Check if subject name already exists for the selected class
        existing_subject = Subject.query.filter_by(name=name.data).join(Subject.classes).filter(Class.id == self.class_id.data).first()
        if existing_subject is not None:
            raise ValidationError('A subject with this name already exists for the selected class.')

class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Create Class')

    def validate_name(self, name):
        class_obj = Class.query.filter_by(name=name.data).first()
        if class_obj is not None:
            raise ValidationError('Please use a different class name.')

class TeacherSubjectForm(FlaskForm):
    subjects = SelectMultipleField('Subjects You Teach', choices=[], validators=[], coerce=int)
    submit = SubmitField('Update Subjects')

class AssignTeacherToSubjectForm(FlaskForm):
    teacher_id = SelectField('Select Teacher', choices=[], validators=[DataRequired()], coerce=int)
    submit = SubmitField('Assign Teacher')

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    subject = SelectField('Subject', choices=[
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('partnership', 'Partnership')
    ], validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')

    class Meta:
        csrf = False