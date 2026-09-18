from app.services.goal_service import (
    calculate_goal_progress,
    calculate_monthly_requirement
)


def generate_recommendation(goal, risk_profile):

    progress = calculate_goal_progress(goal)

    monthly_required = calculate_monthly_requirement(goal)

    category = risk_profile.category

    if category == "CONSERVATIVE":
        allocation = {
            "equity": 30,
            "bonds": 60,
            "cash": 10
        }

    elif category == "MODERATE":
        allocation = {
            "equity": 60,
            "bonds": 30,
            "cash": 10
        }

    else:
        allocation = {
            "equity": 80,
            "bonds": 15,
            "cash": 5
        }

    if progress["progress_percentage"] < 25:
        action = "Increase monthly investment"

    elif progress["progress_percentage"] < 75:
        action = "Continue current investment plan"

    else:
        action = "Review and rebalance portfolio"

    return {
        "goal": goal.name,
        "risk_category": category,
        "progress_percentage":
            progress["progress_percentage"],
        "remaining_amount":
            progress["remaining_amount"],
        "monthly_required":
            monthly_required,
        "suggested_allocation": allocation,
        "recommended_action": action
    }