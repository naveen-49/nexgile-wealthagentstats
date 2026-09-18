from datetime import datetime

from app.extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    household_id = db.Column(
        db.Integer,
        db.ForeignKey("households.id"),
        nullable=False
    )

    first_name = db.Column(
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        db.String(50),
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    date_of_birth = db.Column(
        db.Date
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="client"
    )

    household = db.relationship(
        "Household",
        backref="clients"
    )