
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.extensions import db

from app.models import (
    Client,
    Account,
    Portfolio
)

from app.services.portfolio_service import (
    calculate_portfolio_value,
    calculate_portfolio_allocation
)

from app.services.performance_service import (
    calculate_portfolio_performance
)

from app.utils.auth import role_required


investment_bp = Blueprint(
    "investment",
    __name__
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_client_by_id(client_id):
    """
    Find a client using the client ID.
    """

    if not client_id:
        return None

    return db.session.get(Client, client_id)


# =========================================================
# ACCOUNTS
# =========================================================

@investment_bp.post("/accounts")
@role_required("ADMIN", "ADVISOR")
def create_account():

    data = request.get_json() or {}

    client_id = data.get("client_id")

    if not client_id:
        return {
            "error": "client_id is required"
        }, 400

    client = get_client_by_id(client_id)

    if not client:
        return {
            "error": "Client not found"
        }, 404

    account_number = data.get("account_number")

    if not account_number:
        return {
            "error": "account_number is required"
        }, 400

    existing_account = Account.query.filter_by(
        account_number=account_number
    ).first()

    if existing_account:
        return {
            "error": "Account number already exists"
        }, 409

    account = Account(
        client_id=client.id,
        account_number=account_number,
        account_type=data.get("account_type"),
        institution=data.get("institution"),
        balance=data.get("balance", 0)
    )

    db.session.add(account)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return {
            "error": "Unable to create account"
        }, 500

    return {
        "message": "Account created",
        "account_id": account.id
    }, 201


# =========================================================
# GET ACCOUNTS
# =========================================================

@investment_bp.get("/accounts")
@role_required("ADMIN", "ADVISOR")
def get_accounts():

    accounts = Account.query.order_by(
        Account.id.desc()
    ).all()

    return [
        {
            "id": account.id,
            "client_id": account.client_id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "institution": account.institution,
            "balance": float(account.balance or 0)
        }
        for account in accounts
    ], 200


# =========================================================
# PORTFOLIOS
# =========================================================

@investment_bp.post("/portfolios")
@role_required("ADMIN", "ADVISOR")
def create_portfolio():

    data = request.get_json() or {}

    client_id = data.get("client_id")

    if not client_id:
        return {
            "error": "client_id is required"
        }, 400

    client = get_client_by_id(client_id)

    if not client:
        return {
            "error": "Client not found"
        }, 404

    name = data.get("name")

    if not name:
        return {
            "error": "Portfolio name is required"
        }, 400

    portfolio = Portfolio(
        client_id=client.id,
        name=name,
        risk_profile=data.get("risk_profile"),
        target_allocation=data.get("target_allocation")
    )

    db.session.add(portfolio)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return {
            "error": "Unable to create portfolio"
        }, 500

    return {
        "message": "Portfolio created",
        "portfolio_id": portfolio.id
    }, 201


# =========================================================
# GET PORTFOLIOS
# =========================================================

@investment_bp.get("/portfolios")
@role_required("ADMIN", "ADVISOR")
def get_portfolios():

    portfolios = Portfolio.query.order_by(
        Portfolio.id.desc()
    ).all()

    return [
        {
            "id": portfolio.id,
            "client_id": portfolio.client_id,
            "name": portfolio.name,
            "risk_profile": portfolio.risk_profile,
            "target_allocation": portfolio.target_allocation
        }
        for portfolio in portfolios
    ], 200


# =========================================================
# CLIENT OWNERSHIP HELPER
# =========================================================

def check_portfolio_access(portfolio):

    claims = get_jwt()
    current_role = claims.get("role")

    user_id = get_jwt_identity()

    # Administrators and advisors can access portfolios
    # according to their assigned permissions.
    if current_role in ["ADMIN", "ADVISOR"]:
        return True

    # Clients can access only their own portfolios.
    if current_role == "CLIENT":

        client = Client.query.filter_by(
            user_id=int(user_id)
        ).first()

        if not client:
            return False

        return portfolio.client_id == client.id

    return False


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

@investment_bp.get(
    "/portfolios/<int:portfolio_id>/summary"
)
@role_required("ADMIN", "ADVISOR", "CLIENT")
def portfolio_summary(portfolio_id):

    portfolio = db.session.get(
        Portfolio,
        portfolio_id
    )

    if not portfolio:
        return {
            "error": "Portfolio not found"
        }, 404

    if not check_portfolio_access(portfolio):
        return {
            "error": "Access denied"
        }, 403

    total_value = calculate_portfolio_value(
        portfolio
    )

    allocation = calculate_portfolio_allocation(
        portfolio
    )

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "total_value": total_value,
        "allocation": allocation
    }, 200


# =========================================================
# PORTFOLIO PERFORMANCE
# =========================================================

@investment_bp.get(
    "/portfolios/<int:portfolio_id>/performance"
)
@role_required("ADMIN", "ADVISOR", "CLIENT")
def portfolio_performance(portfolio_id):

    portfolio = db.session.get(
        Portfolio,
        portfolio_id
    )

    if not portfolio:
        return {
            "error": "Portfolio not found"
        }, 404

    if not check_portfolio_access(portfolio):
        return {
            "error": "Access denied"
        }, 403

    performance = calculate_portfolio_performance(
        portfolio
    )

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        **performance
    }, 200