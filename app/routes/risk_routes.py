from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Client, RiskProfile
from app.services.risk_service import calculate_risk_score
from app.utils.auth import role_required
from app.models import Portfolio

risk_bp = Blueprint("risk", __name__)


@risk_bp.post("/")
@role_required("CLIENT")
def create_risk_profile():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    data = request.get_json()

    answers = data.get("answers", [])

    if not answers:
        return {
            "error": "answers are required"
        }, 400

    try:
        score, category = calculate_risk_score(
            answers
        )
    except (ValueError, TypeError):
        return {
            "error": "answers must contain numbers"
        }, 400

    profile = RiskProfile.query.filter_by(
        client_id=client.id
    ).first()

    if profile:
        profile.score = score
        profile.category = category
    else:
        profile = RiskProfile(
            client_id=client.id,
            score=score,
            category=category
        )

        db.session.add(profile)
        # Update portfolio risk profile
        portfolio = Portfolio.query.filter_by(
    client_id=client.id
).first()

        if portfolio:
         portfolio.risk_profile = category

    
    db.session.commit()

    return {
        "message": "Risk profile created",
        "score": score,
        "category": category
    }, 201


@risk_bp.get("/")
@role_required("CLIENT", "ADMIN", "ADVISOR")
def get_risk_profile():

    user_id = get_jwt_identity()

    client = Client.query.filter_by(
        user_id=user_id
    ).first()

    if not client:
        return {
            "error": "Client profile not found"
        }, 404

    profile = RiskProfile.query.filter_by(
        client_id=client.id
    ).first()

    if not profile:
        return {
            "error": "Risk profile not found"
        }, 404

    return {
        "client_id": client.id,
        "score": profile.score,
        "category": profile.category
    }