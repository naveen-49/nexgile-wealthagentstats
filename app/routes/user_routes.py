from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint("user", __name__)


@user_bp.get("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    return {
        "message": "Authenticated user",
        "user_id": user_id
    }