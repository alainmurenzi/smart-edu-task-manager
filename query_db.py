import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('instance/smart_edu.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Count unread for all users
print("=== Unread Notifications by User ===")
for user_id in [7, 25]:  # admin and Emmy
    cursor.execute("SELECT COUNT(*) FROM notification WHERE user_id=? AND is_read=0", (user_id,))
    count = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM user WHERE id=?", (user_id,))
    name = cursor.fetchone()[0]
    print(f"  User {user_id} ({name}): {count} unread")

# Check if there are any notifications for other users
cursor.execute("SELECT DISTINCT user_id FROM notification WHERE is_read=0")
unread_users = cursor.fetchall()
print(f"\nUsers with unread notifications: {[u['user_id'] for u in unread_users]}")

conn.close()
