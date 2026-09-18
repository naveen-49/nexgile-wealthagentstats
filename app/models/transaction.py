from datetime import datetime

from app.extensions import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts.id"),
        nullable=False
    )

    holding_id = db.Column(
        db.Integer,
        db.ForeignKey("holdings.id"),
        nullable=True
    )

    transaction_type = db.Column(
        db.String(20),
        nullable=False
    )

    quantity = db.Column(
        db.Numeric(18, 6),
        nullable=True
    )

    price = db.Column(
        db.Numeric(15, 2),
        nullable=True
    )

    amount = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    transaction_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    account = db.relationship(
        "Account",
        backref="transactions"
    )

    holding = db.relationship(
        "Holding",
        backref="transactions"
    )