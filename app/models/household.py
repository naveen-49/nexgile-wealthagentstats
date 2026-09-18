from datetime import datetime

from app.extensions import db


class Household(db.Model):
    __tablename__ = "households"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(
        db.String(100),
        nullable=False
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