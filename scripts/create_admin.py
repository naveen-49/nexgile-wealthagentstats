from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Role, User


app = create_app()

with app.app_context():

    role = Role.query.filter_by(name="ADMIN").first()

    if not role:
        print("ERROR: ADMIN role does not exist.")
        print("Create the ADMIN role first.")
        raise SystemExit(1)

    username = "admin"
    email = "admin@nexgile.com"
    password = "Admin@123"

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        print("Admin user already exists.")
        print("Email:", email)
        raise SystemExit(0)

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role_id=role.id
    )

    db.session.add(user)
    db.session.commit()

    print("ADMIN user created successfully.")
    print("Username:", username)
    print("Email:", email)
    print("Password:", password)
    print("User ID:", user.id)