from flask import Blueprint, request

from app.extensions import db
from app.models import Household
from app.utils.auth import role_required

household_bp = Blueprint("household", __name__)


@household_bp.post("/")
@role_required("ADMIN", "ADVISOR")
def create_household():
    data = request.get_json()

    household = Household(
        name=data.get("name")
    )

    db.session.add(household)
    db.session.commit()

    return {
        "message": "Household created",
        "household_id": household.id
    }, 201


@household_bp.get("/")
@role_required("ADMIN", "ADVISOR")
def get_households():
    households = Household.query.all()

    return [
        {
            "id": household.id,
            "name": household.name
        }
        for household in households
    ]