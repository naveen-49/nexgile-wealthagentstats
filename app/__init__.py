from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, jwt


def create_app():

    app = Flask(__name__)

    # =====================================================
    # CONFIGURATION
    # =====================================================

    app.config.from_object(Config)

    # =====================================================
    # CORS
    # =====================================================

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]
            }
        },
        allow_headers=[
            "Content-Type",
            "Authorization"
        ],
        methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS"
        ]
    )

    # =====================================================
    # INITIALIZE EXTENSIONS
    # =====================================================

    db.init_app(app)
    migrate.init_app(app)
    jwt.init_app(app)

    # =====================================================
    # IMPORT MODELS
    # =====================================================

    from app.models import (
        Role,
        User,
        Household,
        Client,
        Account,
        Portfolio,
        Holding,
        Transaction,
        FinancialGoal,
        RiskProfile,
        AuditLog
    )

    # =====================================================
    # IMPORT ROUTES
    # =====================================================

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.client_routes import client_bp
    from app.routes.household_routes import household_bp
    from app.routes.risk_routes import risk_bp
    from app.routes.recommendation_routes import recommendation_bp
    from app.routes.investment_routes import investment_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.goal_routes import goal_bp
    from app.routes.audit_routes import audit_bp
    from app.routes.holding import holding_bp
    from app.routes.transaction_routes import transaction_bp
    from app.routes.portfolio_routes import portfolio_bp
    # =====================================================
    # REGISTER BLUEPRINTS
    # =====================================================

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        user_bp,
        url_prefix="/api/users"
    )

    app.register_blueprint(
        client_bp,
        url_prefix="/api/clients"
    )

    app.register_blueprint(
        household_bp,
        url_prefix="/api/households"
    )

    app.register_blueprint(
        investment_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        dashboard_bp,
        url_prefix="/api/dashboard"
    )

    app.register_blueprint(
        goal_bp,
        url_prefix="/api/goals"
    )

    app.register_blueprint(
        risk_bp,
        url_prefix="/api/risk"
    )

    app.register_blueprint(
        recommendation_bp,
        url_prefix="/api/recommendations"
    )

    app.register_blueprint(
        audit_bp,
        url_prefix="/api/audit"
    )

    app.register_blueprint(
        holding_bp,
        url_prefix="/api/holdings"
    )

    app.register_blueprint(
        transaction_bp,
        url_prefix="/api/transactions"
    )
    app.register_blueprint(
    portfolio_bp,
    url_prefix="/api/portfolios"
)
    # =====================================================
    # HOME
    # =====================================================

    @app.route("/")
    def home():

        return {
            "message": "Nexgile WealthAgent API is running"
        }

    # =====================================================
    # FRONTEND
    # =====================================================

    @app.get("/app")
    def frontend():

        return app.send_static_file("index.html")

    # =====================================================
    # 404 ERROR
    # =====================================================

    @app.errorhandler(404)
    def not_found(error):

        return {
            "error": "Resource not found"
        }, 404

    # =====================================================
    # 500 ERROR
    # =====================================================

    @app.errorhandler(500)
    def internal_error(error):

        db.session.rollback()

        return {
            "error": "Internal server error"
        }, 500

    return app