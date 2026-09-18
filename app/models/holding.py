from datetime import datetime

from app.extensions import db


class Holding(db.Model):
    __tablename__ = "holdings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    portfolio_id = db.Column(
        db.Integer,
        db.ForeignKey("portfolios.id"),
        nullable=False
    )

    symbol = db.Column(
        db.String(20),
        nullable=False
    )

    quantity = db.Column(
        db.Numeric(18, 6),
        nullable=False
    )

    average_cost = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    current_price = db.Column(
        db.Numeric(15, 2),
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    portfolio = db.relationship(
        "Portfolio",
        backref="holdings"
    )