from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Client, Holding, Portfolio
from app.utils.auth import role_required


holding_bp = Blueprint("holding", __name__)


# =========================================================
# CREATE HOLDING
# =========================================================

@holding_bp.post("/")
@role_required("ADMIN", "ADVISOR")
def create_holding():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    portfolio_id = data.get("portfolio_id")
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    average_cost = data.get("average_cost")
    current_price = data.get("current_price", 0)

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------

    if (
        not portfolio_id
        or not symbol
        or quantity is None
        or average_cost is None
    ):
        return jsonify({
            "error": (
                "portfolio_id, symbol, quantity "
                "and average_cost are required"
            )
        }), 400

    # -----------------------------------------------------
    # VALIDATE NUMBERS
    # -----------------------------------------------------

    try:
        quantity = float(quantity)
        average_cost = float(average_cost)
        current_price = float(current_price)

    except (ValueError, TypeError):

        return jsonify({
            "error": (
                "quantity, average_cost and "
                "current_price must be numbers"
            )
        }), 400

    # -----------------------------------------------------
    # CHECK PORTFOLIO
    # -----------------------------------------------------

    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        return jsonify({
            "error": "Portfolio not found"
        }), 404

    # -----------------------------------------------------
    # VALIDATE VALUES
    # -----------------------------------------------------

    if quantity <= 0:

        return jsonify({
            "error": "Quantity must be greater than 0"
        }), 400

    if average_cost < 0 or current_price < 0:

        return jsonify({
            "error": "Prices cannot be negative"
        }), 400

    # -----------------------------------------------------
    # CREATE HOLDING
    # -----------------------------------------------------

    holding = Holding(
        portfolio_id=portfolio_id,
        symbol=symbol.upper(),
        quantity=quantity,
        average_cost=average_cost,
        current_price=current_price
    )

    db.session.add(holding)
    db.session.commit()

    return jsonify({
        "message": "Holding created",
        "holding_id": holding.id
    }), 201


# =========================================================
# GET ALL HOLDINGS
# ADMIN / ADVISOR
# =========================================================

@holding_bp.get("/")
@role_required("ADMIN", "ADVISOR")
def get_holdings():

    holdings = Holding.query.all()

    return jsonify([
        {
            "id": holding.id,
            "portfolio_id": holding.portfolio_id,
            "symbol": holding.symbol,
            "quantity": float(holding.quantity),
            "average_cost": float(holding.average_cost),
            "current_price": float(holding.current_price),
            "market_value": float(
                holding.quantity * holding.current_price
            )
        }
        for holding in holdings
    ]), 200


# =========================================================
# GET CLIENT HOLDINGS
# =========================================================

@holding_bp.get("/client")
@role_required("CLIENT")
def get_client_holdings():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:

        return jsonify({
            "error": "Client profile not found"
        }), 404

    holdings = (
        Holding.query
        .join(Portfolio)
        .filter(
            Portfolio.client_id == client.id
        )
        .order_by(
            Holding.symbol.asc()
        )
        .all()
    )

    return jsonify([
        {
            "id": holding.id,

            "portfolio_id":
                holding.portfolio_id,

            "symbol":
                holding.symbol,

            "quantity":
                float(holding.quantity),

            "average_cost":
                float(holding.average_cost),

            "current_price":
                float(holding.current_price),

            "market_value":
                float(
                    holding.quantity *
                    holding.current_price
                )
        }

        for holding in holdings

    ]), 200