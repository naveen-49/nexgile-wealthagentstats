from flask import Blueprint
from flask_jwt_extended import get_jwt_identity

from app.models import (
    Client,
    Account,
    Portfolio,
    Holding,
    FinancialGoal,
    RiskProfile
)

from app.services.goal_service import (
    calculate_goal_progress,
    calculate_monthly_requirement
)

from app.services.portfolio_service import (
    calculate_portfolio_value
)

from app.utils.auth import role_required


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


# =========================================================
# ADVISOR DASHBOARD
# =========================================================

@dashboard_bp.get("/advisor")
@role_required("ADMIN", "ADVISOR")
def advisor_dashboard():

    clients = Client.query.count()

    accounts = Account.query.count()

    portfolios = Portfolio.query.count()

    holdings = Holding.query.count()

    total_assets = sum(
        float(account.balance)
        for account in Account.query.all()
    )

    return {
        "clients": clients,
        "accounts": accounts,
        "portfolios": portfolios,
        "holdings": holdings,
        "total_assets": total_assets
    }


# =========================================================
# CLIENT DASHBOARD
# =========================================================

@dashboard_bp.get("/client")
@role_required("CLIENT")
def client_dashboard():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:

        return {
            "error": "Client profile not found"
        }, 404

    accounts = Account.query.filter_by(
        client_id=client.id
    ).all()

    portfolios = Portfolio.query.filter_by(
        client_id=client.id
    ).all()

    total_balance = sum(
        float(account.balance)
        for account in accounts
    )

    return {
        "client_id": client.id,

        "name": (
            f"{client.first_name} "
            f"{client.last_name}"
        ),

        "accounts": len(accounts),

        "portfolios": len(portfolios),

        "total_balance": total_balance
    }


# =========================================================
# FULL CLIENT DASHBOARD
# =========================================================

@dashboard_bp.get("/client/full")
@role_required("CLIENT")
def client_full_dashboard():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:

        return {
            "error": "Client profile not found"
        }, 404

    # -----------------------------------------------------
    # ACCOUNTS
    # -----------------------------------------------------

    accounts = Account.query.filter_by(
        client_id=client.id
    ).all()

    # -----------------------------------------------------
    # PORTFOLIOS
    # -----------------------------------------------------

    portfolios = Portfolio.query.filter_by(
        client_id=client.id
    ).all()

    # -----------------------------------------------------
    # GOALS
    # -----------------------------------------------------

    goals = FinancialGoal.query.filter_by(
        client_id=client.id
    ).all()

    # -----------------------------------------------------
    # RISK PROFILE
    # -----------------------------------------------------

    risk_profile = RiskProfile.query.filter_by(
        client_id=client.id
    ).first()

    # -----------------------------------------------------
    # CASH
    # -----------------------------------------------------

    total_cash = sum(
        float(account.balance)
        for account in accounts
    )

    # -----------------------------------------------------
    # PORTFOLIO VALUE
    # -----------------------------------------------------

    total_portfolio_value = sum(
        calculate_portfolio_value(portfolio)
        for portfolio in portfolios
    )

    # -----------------------------------------------------
    # GOAL DATA
    # -----------------------------------------------------

    goal_data = []

    for goal in goals:

        goal_info = {
            "id": goal.id,
            "name": goal.name,

            **calculate_goal_progress(goal),

            "monthly_requirement":
                calculate_monthly_requirement(goal)
        }

        # -------------------------------------------------
        # TARGET DATE
        # -------------------------------------------------

        if goal.target_date:

            goal_info["target_date"] = (
                goal.target_date.isoformat()
            )

        else:

            goal_info["target_date"] = None

        # -------------------------------------------------
        # PRIORITY
        # -------------------------------------------------

        goal_info["priority"] = (
            goal.priority
            if goal.priority
            else "MEDIUM"
        )

        goal_data.append(goal_info)

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "client": {
            "id": client.id,

            "name": (
                f"{client.first_name} "
                f"{client.last_name}"
            )
        },

        "financial_summary": {

            "cash":
                total_cash,

            "portfolio_value":
                total_portfolio_value,

            "total_assets":
                total_cash +
                total_portfolio_value
        },

        "risk_profile": (

            {
                "score":
                    risk_profile.score,

                "category":
                    risk_profile.category
            }

            if risk_profile

            else None
        ),

        "goals":
            goal_data
    }