from datetime import datetime

from app.extensions import db


class RiskProfile(db.Model):
    __tablename__ = "risk_profiles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False,
        unique=True
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )

    category = db.Column(
        db.String(30),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = db.relationship(
        "Client",
        backref=db.backref(
            "risk_profile",
            uselist=False
        )
    )