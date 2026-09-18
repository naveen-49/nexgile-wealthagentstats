from datetime import datetime

from app.extensions import db


class Portfolio(db.Model):
    __tablename__ = "portfolios"

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

    risk_profile = db.Column(
        db.String(50)
    )

    target_allocation = db.Column(
        db.JSON
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = db.relationship(
        "Client",
        backref="portfolios"
    )
    