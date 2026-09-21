
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.models import (
    Client,
    Account,
    Holding,
    Transaction
)

from app.services.transaction_service import (
    process_transaction
)

from app.utils.auth import role_required


transaction_bp = Blueprint(
    "transaction",
    __name__
)


# =========================================================
# GET CURRENT USER ACCOUNT
# =========================================================

@transaction_bp.get("/account/")
@role_required("CLIENT")
def get_my_account():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    account = Account.query.filter_by(
        client_id=client.id
    ).first()

    if not account:
        return {
            "error": "Account not found"
        }, 404

    return {
        "id": account.id,
        "account_number": account.account_number,
        "account_type": account.account_type,
        "institution": account.institution,
        "balance": float(account.balance)
    }, 200


# =========================================================
# CREATE TRANSACTION
# =========================================================
@transaction_bp.post("/")
@role_required("CLIENT")
def create_transaction():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    data = request.get_json() or {}

    account_id = data.get("account_id")
    holding_id = data.get("holding_id")
    symbol = data.get("symbol")
    transaction_type = data.get("transaction_type")
    quantity = data.get("quantity")
    price = data.get("price")
    amount = data.get("amount")

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------

    if not account_id:
        return {
            "error": "account_id is required"
        }, 400

    if not transaction_type:
        return {
            "error": "transaction_type is required"
        }, 400

    if amount is None:
        return {
            "error": "amount is required"
        }, 400

    transaction_type = str(
        transaction_type
    ).upper()

    allowed_types = {
        "BUY",
        "SELL",
        "DEPOSIT",
        "WITHDRAWAL",
        "DIVIDEND"
    }

    if transaction_type not in allowed_types:
        return {
            "error": "Invalid transaction type"
        }, 400

    # -----------------------------------------------------
    # CHECK ACCOUNT OWNERSHIP
    # -----------------------------------------------------

    account = Account.query.filter_by(
        id=account_id,
        client_id=client.id
    ).first()

    if not account:
        return {
            "error": "Account not found"
        }, 404

    # -----------------------------------------------------
    # CONVERT NUMBERS
    # -----------------------------------------------------

    try:

        amount = Decimal(str(amount))

        if quantity is not None:
            quantity = Decimal(str(quantity))

        if price is not None:
            price = Decimal(str(price))

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        return {
            "error": (
                "quantity, price and amount "
                "must be valid numbers"
            )
        }, 400

    # -----------------------------------------------------
    # AMOUNT VALIDATION
    # -----------------------------------------------------

    if amount <= 0:
        return {
            "error": "amount must be greater than 0"
        }, 400

    # -----------------------------------------------------
    # BUY VALIDATION
    # -----------------------------------------------------

    if transaction_type == "BUY":

        if not symbol:
            return {
                "error": "symbol is required for BUY"
            }, 400

        if quantity is None or quantity <= 0:
            return {
                "error": (
                    "quantity must be greater "
                    "than 0"
                )
            }, 400

        if price is None or price <= 0:
            return {
                "error": (
                    "price must be greater "
                    "than 0"
                )
            }, 400

    # -----------------------------------------------------
    # SELL VALIDATION
    # -----------------------------------------------------

    if transaction_type == "SELL":

        if not holding_id:
            return {
                "error": (
                    "holding_id is required "
                    "for SELL"
                )
            }, 400

        if quantity is None or quantity <= 0:
            return {
                "error": (
                    "quantity must be greater "
                    "than 0"
                )
            }, 400

        if price is None or price <= 0:
            return {
                "error": (
                    "price must be greater "
                    "than 0"
                )
            }, 400

    # -----------------------------------------------------
    # CHECK HOLDING
    # -----------------------------------------------------

    if holding_id:

        holding = Holding.query.filter_by(
            id=holding_id
        ).first()

        if not holding:
            return {
                "error": "Holding not found"
            }, 404

        if holding.portfolio.client_id != client.id:
            return {
                "error": (
                    "Access denied for this holding"
                )
            }, 403

    # -----------------------------------------------------
    # PROCESS TRANSACTION
    # -----------------------------------------------------

    try:

        transaction = process_transaction(
            account_id=account_id,
            holding_id=holding_id,
            symbol=symbol,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            amount=amount,
            client_id=client.id
        )

    except ValueError as error:

        db.session.rollback()

        return {
            "error": str(error)
        }, 400

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "message": "Transaction created",
        "transaction_id": transaction.id
    }, 201
# =========================================================
# GET TRANSACTIONS
# =========================================================

@transaction_bp.get("/")
@role_required("CLIENT")
def get_transactions():

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

    account_ids = [
        account.id
        for account in accounts
    ]

    if not account_ids:
        return [], 200

    transactions = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(
        Transaction.transaction_date.desc()
    ).all()

    return [
        {
            "id": transaction.id,

            "account_id":
                transaction.account_id,

            "holding_id":
                transaction.holding_id,

            "transaction_type":
                transaction.transaction_type,

            "quantity": (
                float(transaction.quantity)
                if transaction.quantity is not None
                else None
            ),

            "price": (
                float(transaction.price)
                if transaction.price is not None
                else None
            ),

            "amount":
                float(transaction.amount),

            "transaction_date":
                transaction.transaction_date.isoformat()
        }

        for transaction in transactions
    ], 200