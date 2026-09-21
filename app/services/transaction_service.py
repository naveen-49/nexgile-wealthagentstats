
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.extensions import db
from app.services.market_service import get_stock_price

from app.models import (
    Account,
    Holding,
    Transaction,
    Portfolio
)


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
    symbol,
    transaction_type,
    quantity,
    price,
    amount,
    client_id=None
):
    """
    Process a transaction for an authorized client.
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

    # Amount is required for non-BUY transactions.
    # BUY amount is calculated automatically.
    if transaction_type != "BUY":

        if amount is None or amount <= 0:
            raise ValueError(
                "Amount must be greater than 0"
            )

    # -----------------------------------------------------
    # GET ACCOUNT
    # -----------------------------------------------------

    account = db.session.get(
        Account,
        account_id
    )

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

        holding = db.session.get(
            Holding,
            holding_id
        )

        if not holding:
            raise ValueError(
                "Holding not found"
            )

        if client_id is not None:

            if holding.portfolio.client_id != client_id:
                raise ValueError(
                    "You are not authorized to use this holding"
                )

    # =====================================================
    # BUY
    # =====================================================

    if transaction_type == "BUY":

        # -------------------------------------------------
        # VALIDATE SYMBOL
        # -------------------------------------------------

        if not symbol:
            raise ValueError(
                "Symbol is required for BUY"
            )

        symbol = symbol.strip().upper()

        # -------------------------------------------------
        # VALIDATE QUANTITY
        # -------------------------------------------------

        if quantity is None or quantity <= 0:
            raise ValueError(
                "Quantity must be greater than 0"
            )

        # -------------------------------------------------
        # FETCH AUTOMATIC MARKET PRICE
        # -------------------------------------------------

        price = Decimal(
            str(get_stock_price(symbol))
        )

        if price <= 0:
            raise ValueError(
                "Invalid market price"
            )

        # -------------------------------------------------
        # CALCULATE AMOUNT AUTOMATICALLY
        # -------------------------------------------------

        amount = (
            quantity * price
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # -------------------------------------------------
        # CHECK ACCOUNT BALANCE
        # -------------------------------------------------

        if account.balance is None:
            account.balance = Decimal("0")

        if account.balance < amount:
            raise ValueError(
                "Insufficient account balance"
            )

        # -------------------------------------------------
        # FIND CLIENT PORTFOLIO
        # -------------------------------------------------

        portfolio = Portfolio.query.filter_by(
            client_id=client_id
        ).first()

        if not portfolio:
            raise ValueError(
                "Portfolio not found"
            )

        # -------------------------------------------------
        # FIND EXISTING HOLDING BY SYMBOL
        # -------------------------------------------------

        if holding is None:

            holding = Holding.query.filter_by(
                portfolio_id=portfolio.id,
                symbol=symbol
            ).first()

        # -------------------------------------------------
        # CREATE NEW HOLDING
        # -------------------------------------------------

        if holding is None:

            holding = Holding(
                portfolio_id=portfolio.id,
                symbol=symbol,
                quantity=quantity,
                average_cost=price,
                current_price=price
            )

            db.session.add(holding)
            db.session.flush()

            holding_id = holding.id

        # -------------------------------------------------
        # UPDATE EXISTING HOLDING
        # -------------------------------------------------

        else:

            old_quantity = Decimal(
                str(holding.quantity)
            )

            old_average_cost = Decimal(
                str(holding.average_cost)
            )

            total_quantity = (
                old_quantity + quantity
            )

            weighted_average = (
                (old_quantity * old_average_cost)
                + (quantity * price)
            ) / total_quantity

            holding.quantity = total_quantity

            holding.average_cost = (
                weighted_average.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )
            )

            holding.current_price = price

            holding_id = holding.id

        # -------------------------------------------------
        # DEDUCT ACCOUNT BALANCE
        # -------------------------------------------------

        account.balance -= amount

    # =====================================================
    # SELL
    # =====================================================

    elif transaction_type == "SELL":

        # -------------------------------------------------
        # VALIDATE HOLDING
        # -------------------------------------------------

        if holding is None:
            raise ValueError(
                "Holding is required for SELL"
            )

        if quantity is None or quantity <= 0:
            raise ValueError(
                "Quantity must be greater than 0"
            )

        if price is None or price <= 0:
            raise ValueError(
                "Price must be greater than 0"
            )

        # -------------------------------------------------
        # VALIDATE HOLDING QUANTITY
        # -------------------------------------------------

        holding_quantity = Decimal(
            str(holding.quantity)
        )

        if quantity > holding_quantity:
            raise ValueError(
                "Insufficient holding quantity"
            )

        # -------------------------------------------------
        # CALCULATE SELL AMOUNT
        # -------------------------------------------------

        amount = (
            quantity * price
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # -------------------------------------------------
        # UPDATE HOLDING QUANTITY
        # -------------------------------------------------

        holding.quantity = (
            holding_quantity - quantity
        )

        holding_id = holding.id

        # -------------------------------------------------
        # ADD MONEY TO ACCOUNT
        # -------------------------------------------------

        if account.balance is None:
            account.balance = Decimal("0")

        account.balance += amount

    # =====================================================
    # DEPOSIT
    # =====================================================

    elif transaction_type == "DEPOSIT":

        account.balance = (
            account.balance or Decimal("0")
        )

        account.balance += amount

    # =====================================================
    # WITHDRAWAL
    # =====================================================

    elif transaction_type == "WITHDRAWAL":

        account.balance = (
            account.balance or Decimal("0")
        )

        if account.balance < amount:
            raise ValueError(
                "Insufficient account balance"
            )

        account.balance -= amount

    # =====================================================
    # DIVIDEND
    # =====================================================

    elif transaction_type == "DIVIDEND":

        account.balance = (
            account.balance or Decimal("0")
        )

        account.balance += amount

    # =====================================================
    # CREATE TRANSACTION
    # =====================================================

    transaction = Transaction(
        account_id=account_id,
        holding_id=holding_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        amount=amount
    )

    db.session.add(transaction)

    # =====================================================
    # COMMIT TRANSACTION
    # =====================================================

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()
        raise

    return transaction