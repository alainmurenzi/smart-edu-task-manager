"""Migration script to add task_classes table for tracking which classes a task is assigned to."""
from app import db
from models.models import task_classes

# Create the task_classes table
task_classes.create(db.engine)

print("task_classes table created successfully!")
print("Note: Existing tasks won't have class assignments.")
print("Please recreate tasks or assign classes to them to enable auto-assignment for new students.")
