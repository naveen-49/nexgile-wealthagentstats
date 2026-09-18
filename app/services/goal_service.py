from datetime import date

from app.models import FinancialGoal


def calculate_goal_progress(goal):
    target = float(goal.target_amount)
    current = float(goal.current_amount)

    if target <= 0:
        percentage = 0
    else:
        percentage = (current / target) * 100

    remaining = max(target - current, 0)

    return {
        "target_amount": target,
        "current_amount": current,
        "remaining_amount": round(remaining, 2),
        "progress_percentage": round(
            min(percentage, 100),
            2
        )
    }


def calculate_monthly_requirement(goal):
    today = date.today()

    months_remaining = (
        (goal.target_date.year - today.year) * 12
        + goal.target_date.month
        - today.month
    )

    if months_remaining <= 0:
        months_remaining = 1

    remaining = max(
        float(goal.target_amount)
        - float(goal.current_amount),
        0
    )

    return round(
        remaining / months_remaining,
        2
    )