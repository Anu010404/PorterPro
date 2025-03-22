"""
Management commands for the Porter Booking System
"""
from werkzeug.security import generate_password_hash
from app import app, db
from models import User

def create_admin(email, username, password):
    """Create an admin user"""
    with app.app_context():
        user = User(
            email=email,
            username=username,
            role='admin'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

if __name__ == "__main__":
    # Example usage:
    # python commands.py create_admin admin@example.com admin password123
    import sys
    if len(sys.argv) != 4:
        print("Usage: python commands.py <email> <username> <password>")
        sys.exit(1)

    _, email, username, password = sys.argv
    create_admin(email, username, password)
    print(f"Admin user '{username}' created successfully!")