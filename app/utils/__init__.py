from functools import wraps

from flask import request, jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt
)


def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            # =================================================
            # CORS PREFLIGHT
            # =================================================

            if request.method == "OPTIONS":
                return "", 200

            # =================================================
            # VERIFY JWT
            # =================================================

            try:
                verify_jwt_in_request()

            except Exception as error:
                return jsonify({
                    "error": str(error)
                }), 401

            # =================================================
            # GET USER ROLE
            # =================================================

            claims = get_jwt()

            user_role = claims.get("role")

            # =================================================
            # CHECK ROLE
            # =================================================

            if user_role not in allowed_roles:

                return jsonify({
                    "error": "Access denied"
                }), 403

            # =================================================
            # RUN ACTUAL ROUTE
            # =================================================

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator