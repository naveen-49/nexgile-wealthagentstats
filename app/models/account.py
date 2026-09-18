from datetime import datetime

from app.extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False
    )

    account_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    account_type = db.Column(
        db.String(50),
        nullable=False
    )

    institution = db.Column(
        db.String(100)
    )

    balance = db.Column(
        db.Numeric(15, 2),
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = db.relationship(
        "Client",
        backref="accounts"
    )