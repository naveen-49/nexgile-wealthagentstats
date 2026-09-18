from flask import Blueprint, request

from app.extensions import db
from app.models import Client, Household
from app.utils.auth import role_required
from flask import request
from app.utils.pagination import paginate_query

client_bp = Blueprint("client", __name__)


@client_bp.post("/")
@role_required("ADMIN", "ADVISOR")
def create_client():
    data = request.get_json()

    household = Household.query.get(data.get("household_id"))

    if not household:
        return {"error": "Household not found"}, 404

    client = Client(
        user_id=data.get("user_id"),
        household_id=household.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        phone=data.get("phone"),
        date_of_birth=data.get("date_of_birth")
    )

    db.session.add(client)
    db.session.commit()

    return {
        "message": "Client created",
        "client_id": client.id
    }, 201


@client_bp.get("/")
@role_required("ADMIN", "ADVISOR")
def get_clients():
    clients = Client.query.all()

    return [
        {
            "id": client.id,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "household_id": client.household_id
        }
        for client in clients
    ]