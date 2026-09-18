
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models import Account, Holding, Transaction


def to_decimal(value, field_name):
    """
    Convert incoming values to Decimal safely.
    """

    if value is None:
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(
            f"{field_name} must be a valid number"
        )


def process_transaction(
    account_id,
    holding_id,
    transaction_type,
    quantity,
    price,
    amount,
    client_id=None
):
    """
    Process a transaction only for an authorized client.

    client_id is used to verify account and holding ownership.
    """

    # -----------------------------------------------------
    # CONVERT VALUES TO DECIMAL
    # -----------------------------------------------------

    amount = to_decimal(amount, "amount")
    quantity = to_decimal(quantity, "quantity")
    price = to_decimal(price, "price")

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if amount is None or amount <= 0:
        raise ValueError(
            "amount must be greater than 0"
        )

    if not transaction_type:
        raise ValueError(
            "Transaction type is required"
        )

    transaction_type = transaction_type.upper()

    allowed_types = {
        "BUY",
        "SELL",
        "DEPOSIT",
        "WITHDRAWAL",
        "DIVIDEND"
    }

    if transaction_type not in allowed_types:
        raise ValueError(
            "Invalid transaction type"
        )

    # -----------------------------------------------------
    # GET ACCOUNT
    # -----------------------------------------------------

    account = db.session.get(Account, account_id)

    if not account:
        raise ValueError(
            "Account not found"
        )

    # -----------------------------------------------------
    # VERIFY ACCOUNT OWNERSHIP
    # -----------------------------------------------------

    if client_id is not None:
        if account.client_id != client_id:
            raise ValueError(
                "You are not authorized to use this account"
            )

    # -----------------------------------------------------
    # GET HOLDING
    # -----------------------------------------------------

    holding = None

    if holding_id is not None:
        holding = db.session.get(Holding, holding_id)

        if not holding:
            raise ValueError(
                "Holding not found"
            )

        # -------------------------------------------------
        # VERIFY HOLDING OWNERSHIP
        # -------------------------------------------------

        if client_id is not None:
            if holding.portfolio.client_id != client_id:
                raise ValueError(
                    "You are not authorized to use this holding"
                )

    # -----------------------------------------------------
    # BUY
    # -----------------------------------------------------

    if transaction_type == "BUY":

        if not holding:
            raise ValueError(
                "Holding is required for BUY"
            )

        if quantity is None or quantity <= 0:
            raise ValueError(
                "quantity must be greater than 0"
            )

        if price is None or price <= 0:
            raise ValueError(
                "price must be greater than 0"
            )

        if account.balance is None:
            account.balance = Decimal("0")

        if account.balance < amount:
            raise ValueError(
                "Insufficient account balance"
            )

        holding.quantity += quantity
        account.balance -= amount

    # -----------------------------------------------------
    # SELL
    # -----------------------------------------------------

    elif transaction_type == "SELL":

        if not holding:
            raise ValueError(
                "Holding is required for SELL"
            )

        if quantity is None or quantity <= 0:
            raise ValueError(
                "quantity must be greater than 0"
            )

        if price is None or price <= 0:
            raise ValueError(
                "price must be greater than 0"
            )

        if holding.quantity < quantity:
            raise ValueError(
                "Insufficient holding quantity"
            )

        holding.quantity -= quantity
        account.balance += amount

    # -----------------------------------------------------
    # DEPOSIT
    # -----------------------------------------------------

    elif transaction_type == "DEPOSIT":

        account.balance += amount

    # -----------------------------------------------------
    # WITHDRAWAL
    # -----------------------------------------------------

    elif transaction_type == "WITHDRAWAL":

        if account.balance < amount:
            raise ValueError(
                "Insufficient account balance"
            )

        account.balance -= amount

    # -----------------------------------------------------
    # DIVIDEND
    # -----------------------------------------------------

    elif transaction_type == "DIVIDEND":

        account.balance += amount

    # -----------------------------------------------------
    # CREATE TRANSACTION
    # -----------------------------------------------------

    transaction = Transaction(
        account_id=account_id,
        holding_id=holding_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        amount=amount
    )

    db.session.add(transaction)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return transaction