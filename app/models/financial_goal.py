from datetime import datetime

from app.extensions import db


class FinancialGoal(db.Model):
    __tablename__ = "financial_goals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    target_amount = db.Column(
        db.Numeric(15, 2),
        nullable=False
    )

    current_amount = db.Column(
        db.Numeric(15, 2),
        default=0,
        nullable=False
    )

    target_date = db.Column(
        db.Date,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        default="MEDIUM",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = db.relationship(
        "Client",
        backref="financial_goals"
    )