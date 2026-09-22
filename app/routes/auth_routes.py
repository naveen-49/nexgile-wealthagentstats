
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_bcrypt import Bcrypt
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.household import Household
from app.models.client import Client
from app.models.account  import Account
from app.models import Portfolio, RiskProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

bcrypt = Bcrypt()


# ===============================
# REGISTER
# ===============================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "message": "Username, email and password are required"
        }), 400

    existing_user = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "message": "Username or email already exists"
        }), 409

    # Find the default CLIENT role
    role = Role.query.filter_by(name="CLIENT").first()

    if not role:
        return jsonify({
            "message": "CLIENT role not found in database"
        }), 500

    # Hash password
    password_hash = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    # Create user
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role_id=role.id,
        is_active=True,
        email_verified=True
    )

    db.session.add(new_user)
    db.session.flush()

    # Create a separate household for this user
    household = Household(
        name=f"{username}'s Household"
    )

    db.session.add(household)
    db.session.flush()

    # Create client linked to this user
    client = Client(
        user_id=new_user.id,
        household_id=household.id,
        first_name=username,
        last_name=""
    )

    db.session.add(client)
    db.session.flush()

    # Create a default risk profile until the user completes a risk assessment
    risk_profile = RiskProfile(
        client_id=client.id,
        score=50,
        category="MODERATE"
    )

    db.session.add(risk_profile)

    # Automatically create a default cash account
    account = Account(
        client_id=client.id,
        account_number=f"ACC-{client.id:04d}-001",
        account_type="CASH",
        institution="Nexgile WealthAgent",
        balance=0.00
    )

    db.session.add(account)

    # Create default portfolio
    portfolio = Portfolio(
        client_id=client.id,
        name="My Investment Portfolio",
        risk_profile=None,
        target_allocation={}
    )

    db.session.add(portfolio)

    db.session.commit()
    return jsonify({
        "message": "Registration successful",
        "user_id": new_user.id
    }), 201
# ===============================
# LOGIN
# ===============================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not user.is_active:
        return jsonify({
            "message": "Account is inactive"
        }), 403
    #if not user.email_verified:
      # return jsonify({
       # "message": "Please verify your email before logging in"
    #}), 403
    # Check password safely
    try:
        print("LOGIN EMAIL:", repr(email))
        print("USER FOUND:", user is not None)

        if user:
             print("HASH START:", user.password_hash[:4])
             print("HASH LENGTH:", len(user.password_hash))

        password_valid = bcrypt.check_password_hash(
    user.password_hash,
    password
)

        print("PASSWORD VALID:", password_valid)

    except ValueError:
        return jsonify({
            "message": (
                "Stored password hash is invalid. "
                "Please register again or reset your password."
            )
        }), 500

    if not password_valid:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    # Verify role exists
    if not user.role:
        return jsonify({
            "message": "User role is not configured"
        }), 500

    # Create JWT token with role
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role.name
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name
        }
    }), 200

# ===============================
# CURRENT USER
# ===============================

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200