
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.models import Client, Portfolio
from app.services.portfolio_service import (
    calculate_portfolio_value,
    calculate_portfolio_allocation
)
from app.utils.auth import role_required


portfolio_bp = Blueprint("portfolio", __name__)


# =========================================================
# GET CLIENT PORTFOLIOS
# =========================================================

@portfolio_bp.get("/client")
@role_required("CLIENT")
def get_client_portfolios():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return jsonify({
            "error": "Client profile not found"
        }), 404

    portfolios = Portfolio.query.filter_by(
        client_id=client.id
    ).all()

    result = []

    for portfolio in portfolios:

        result.append({
            "id": portfolio.id,
            "name": portfolio.name,
            "risk_profile": portfolio.risk_profile,
            "target_allocation": portfolio.target_allocation,
            "total_value": calculate_portfolio_value(
                portfolio
            ),
            "allocation": calculate_portfolio_allocation(
                portfolio
            )
        })

    return jsonify(result), 200