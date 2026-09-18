from app.models import Client


def get_client_for_user(user_id):
    return Client.query.filter_by(user_id=user_id).first()