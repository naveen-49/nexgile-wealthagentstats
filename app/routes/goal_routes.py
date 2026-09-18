from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Client, FinancialGoal

from app.services.audit_service import create_audit_log
from flask import request
from app.utils.pagination import paginate_query

from app.services.goal_service import (
    calculate_goal_progress,
    calculate_monthly_requirement
)

from app.utils.auth import role_required

from app.utils.validators import (
    required_fields,
    positive_number
)


goal_bp = Blueprint(
    "goal",
    __name__
)


# =========================================================
# CREATE FINANCIAL GOAL
# =========================================================

@goal_bp.post("/")
@role_required("ADMIN", "ADVISOR", "CLIENT")
def create_goal():

    data = request.get_json()

    if not data:
        return {
            "error": "Request body is required"
        }, 400

    missing = required_fields(
        data,
        [
            "name",
            "target_amount",
            "target_date"
        ]
    )

    if missing:
        return {
            "error": "Missing required fields",
            "fields": missing
        }, 400

    if not positive_number(
        data["target_amount"]
    ):
        return {
            "error": "target_amount must be greater than 0"
        }, 400

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    try:

        target_date = datetime.strptime(
            data["target_date"],
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):

        return {
            "error": "target_date must be YYYY-MM-DD"
        }, 400

    goal = FinancialGoal(
        client_id=client.id,
        name=data["name"],
        target_amount=data["target_amount"],
        current_amount=data.get(
            "current_amount",
            0
        ),
        target_date=target_date,
        priority=data.get(
            "priority",
            "MEDIUM"
        )
    )

    db.session.add(goal)

    # Get goal.id before commit
    db.session.flush()

    create_audit_log(
        user_id=user_id,
        action="CREATE_GOAL",
        entity_type="FinancialGoal",
        entity_id=goal.id,
        description=(
            f"Created financial goal: "
            f"{goal.name}"
        )
    )

    db.session.commit()

    return {
        "message": "Financial goal created",
        "goal_id": goal.id
    }, 201


# =========================================================
# GET FINANCIAL GOALS
# =========================================================

@goal_bp.get("/")
@role_required("ADMIN", "ADVISOR", "CLIENT")
def get_goals():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    goals = FinancialGoal.query.filter_by(
        client_id=client.id
    ).all()

    return [
        {
            "id": goal.id,

            "name": goal.name,

            "target_amount": float(
                goal.target_amount
            ),

            "current_amount": float(
                goal.current_amount
            ),

            "target_date":
                goal.target_date.isoformat(),

            "priority":
                goal.priority,

            "progress":
                calculate_goal_progress(goal),

            "monthly_requirement":
                calculate_monthly_requirement(goal)
        }

        for goal in goals
    ]