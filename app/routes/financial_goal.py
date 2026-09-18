from datetime import datetime

from flask import Blueprint, request

from app.extensions import db
from app.models import Client, FinancialGoal
from app.services.goal_service import (
    calculate_goal_progress,
    calculate_monthly_requirement
)
from app.utils.auth import role_required
from flask_jwt_extended import get_jwt_identity


goal_bp = Blueprint("goal", __name__)


@goal_bp.post("/")
@role_required("CLIENT")
def create_goal():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    data = request.get_json()

    if not data:
        return {
            "error": "JSON body is required"
        }, 400

    name = data.get("name")
    target_amount = data.get("target_amount")
    current_amount = data.get("current_amount", 0)
    target_date = data.get("target_date")
    priority = data.get("priority", "MEDIUM")

    if not name or target_amount is None or not target_date:
        return {
            "error": "name, target_amount and target_date are required"
        }, 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount)

        if target_amount <= 0:
            return {
                "error": "target_amount must be greater than 0"
            }, 400

        if current_amount < 0:
            return {
                "error": "current_amount cannot be negative"
            }, 400

        target_date = datetime.strptime(
            target_date,
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):
        return {
            "error": "Invalid amount or date format"
        }, 400

    goal = FinancialGoal(
        client_id=client.id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        priority=priority
    )

    db.session.add(goal)
    db.session.commit()

    return {
        "message": "Financial goal created",
        "goal_id": goal.id
    }, 201


@goal_bp.get("/")
@role_required("CLIENT")
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
            "target_amount": float(goal.target_amount),
            "current_amount": float(goal.current_amount),
            "target_date": goal.target_date.isoformat(),
            "priority": goal.priority,
            "progress": calculate_goal_progress(goal),
            "monthly_requirement":
                calculate_monthly_requirement(goal)
        }
        for goal in goals
    ], 200