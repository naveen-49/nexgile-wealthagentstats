from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.models import (
    Client,
    FinancialGoal,
    RiskProfile
)

from app.services.goal_service import (
    calculate_goal_progress,
    calculate_monthly_requirement
)

from app.utils.auth import role_required


recommendation_bp = Blueprint(
    "recommendation",
    __name__
)


# =========================================================
# GET WEALTH RECOMMENDATION
# =========================================================

@recommendation_bp.route(
    "/<int:goal_id>",
    methods=["GET", "OPTIONS"]
)
@role_required("ADMIN", "ADVISOR", "CLIENT")
def get_recommendation(goal_id):

    # -----------------------------------------------------
    # CORS PREFLIGHT
    # -----------------------------------------------------

    if request.method == "OPTIONS":
        return "", 200

    # -----------------------------------------------------
    # GET LOGGED-IN USER
    # -----------------------------------------------------

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    # -----------------------------------------------------
    # GET CLIENT GOAL
    # -----------------------------------------------------

    goal = FinancialGoal.query.filter_by(
        id=goal_id,
        client_id=client.id
    ).first()

    if not goal:
        return {
            "error": "Financial goal not found"
        }, 404

    # -----------------------------------------------------
    # GET RISK PROFILE
    # -----------------------------------------------------

    risk_profile = RiskProfile.query.filter_by(
        client_id=client.id
    ).first()

    if not risk_profile:
        return {
            "error": "Risk profile not found"
        }, 404

    # -----------------------------------------------------
    # GOAL CALCULATIONS
    # -----------------------------------------------------

    progress = calculate_goal_progress(goal)

    monthly_requirement = (
        calculate_monthly_requirement(goal)
    )

    # -----------------------------------------------------
    # NORMALIZE VALUES
    # -----------------------------------------------------

    progress_percentage = float(
        progress.get("progress_percentage", 0)
    )

    target_amount = float(
        progress.get("target_amount", 0)
    )

    current_amount = float(
        progress.get("current_amount", 0)
    )

    remaining_amount = float(
        progress.get("remaining_amount", 0)
    )

    monthly_requirement = float(
        monthly_requirement
    )

    # -----------------------------------------------------
    # RISK CATEGORY
    # -----------------------------------------------------

    category = str(
        risk_profile.category
    ).upper()

    # -----------------------------------------------------
    # ASSET ALLOCATION
    # -----------------------------------------------------

    if category == "CONSERVATIVE":

        allocation = {
            "equity": 30,
            "bonds": 50,
            "cash": 20
        }

    elif category == "MODERATE":

        allocation = {
            "equity": 60,
            "bonds": 30,
            "cash": 10
        }

    elif category == "AGGRESSIVE":

        allocation = {
            "equity": 80,
            "bonds": 15,
            "cash": 5
        }

    else:

        allocation = {
            "equity": 50,
            "bonds": 30,
            "cash": 20
        }

    # -----------------------------------------------------
    # RECOMMENDATION LOGIC
    # -----------------------------------------------------

    if progress_percentage >= 100:

        action = "Goal achieved"

        reason = (
            "Your current amount has reached or exceeded "
            "your target amount."
        )

    elif progress_percentage < 10 and monthly_requirement > 0:

        action = "Increase monthly investment"

        reason = (
            "Goal progress is currently low compared "
            "with the target amount. A higher monthly "
            "investment may be required to reach the goal."
        )

    elif progress_percentage < 50 and monthly_requirement > 0:

        action = "Increase monthly investment"

        reason = (
            "Less than half of the goal has been completed. "
            "Maintaining a consistent monthly investment "
            "is important to improve progress."
        )

    elif progress_percentage >= 50 and monthly_requirement > 0:

        action = "Maintain monthly investment"

        reason = (
            "Your goal has made meaningful progress. "
            "Continue investing consistently toward "
            "the remaining amount."
        )

    else:

        action = "Goal is on track"

        reason = (
            "Based on the available goal information, "
            "the goal does not currently require an "
            "additional monthly investment."
        )

    # -----------------------------------------------------
    # RISK-SPECIFIC GUIDANCE
    # -----------------------------------------------------

    if category == "CONSERVATIVE":

        risk_guidance = (
            "Focus on capital preservation and maintain "
            "a higher allocation toward bonds and cash."
        )

    elif category == "MODERATE":

        risk_guidance = (
            "Use a balanced approach between growth assets "
            "and relatively stable investments."
        )

    elif category == "AGGRESSIVE":

        risk_guidance = (
            "A higher equity allocation can provide greater "
            "growth potential but also involves higher risk."
        )

    else:

        risk_guidance = (
            "Use a diversified allocation until a clearer "
            "risk profile is available."
        )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "goal": {
            "id": goal.id,
            "name": goal.name,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "remaining_amount": remaining_amount,
            "progress_percentage": progress_percentage
        },

        "risk_profile": {
            "score": risk_profile.score,
            "category": risk_profile.category
        },

        "monthly_requirement": monthly_requirement,

        "suggested_allocation": allocation,

        "recommendation": {
            "action": action,
            "reason": reason,
            "risk_guidance": risk_guidance
        }
    }, 200