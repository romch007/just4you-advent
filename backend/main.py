import os

from flask import Flask
from flask_cors import CORS
from argon2 import PasswordHasher

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Base, User
from routes.auth import auth_bp
from routes.calendar import calendar_bp

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "https://advent.logan-lucas.com"])

app.register_blueprint(auth_bp)
app.register_blueprint(calendar_bp)

# Configuration
app.config["SECRET"] = os.getenv("SECRET", "ForGodSakeProvideASecret")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///advent_calendar.db")

app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize Argon2 password hasher
ph = PasswordHasher()
app.config["PASSWORD_HASHER"] = ph

# Database setup
engine = create_engine(app.config["DATABASE_URL"])
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
app.config["DB_SESSION"] = Session


def bootstrap_admin():
    username = os.getenv("BOOTSTRAP_ADMIN_USERNAME")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")

    if not username or not password:
        print("No bootstrap admin credentials found in environment variables")
        return

    session = Session()
    try:
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            print(f"Bootstrap admin user '{username}' already exists")
            return

        # Hash password and create admin user
        hashed_password = ph.hash(password)
        admin_user = User(
            # calendar_id=calendar.id,
            username=username,
            password=hashed_password,
            name="Bootstrap Admin",
            is_admin=True,
        )
        session.add(admin_user)
        session.commit()
        print(f"Bootstrap admin user '{username}' created successfully")
    except Exception as e:
        session.rollback()
        print(f"Error creating bootstrap admin: {e}")
    finally:
        session.close()


bootstrap_admin()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session at the end of the request."""
    Session.remove()


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
