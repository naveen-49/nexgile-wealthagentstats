from functools import wraps

from flask import request

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

                return {
                    "error": str(error)
                }, 401

            # =================================================
            # GET JWT CLAIMS
            # =================================================

            claims = get_jwt()

            user_role = claims.get("role")

            # =================================================
            # NORMALIZE ROLE
            # =================================================

            if user_role:

                user_role = str(
                    user_role
                ).upper().strip()

            allowed_roles_normalized = [
                str(role).upper().strip()
                for role in allowed_roles
            ]

            # =================================================
            # CHECK ROLE
            # =================================================

            if user_role not in allowed_roles_normalized:

                return {
                    "error": "Access denied",
                    "user_role": user_role,
                    "allowed_roles":
                        allowed_roles_normalized
                }, 403

            # =================================================
            # RUN ROUTE
            # =================================================

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator