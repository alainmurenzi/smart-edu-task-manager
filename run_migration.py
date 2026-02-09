from migrate_add_assigned_teacher import migrate
from app import create_app

app = create_app()
with app.app_context():
    migrate()
