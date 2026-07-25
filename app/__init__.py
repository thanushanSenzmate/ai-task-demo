import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.health import health_bp

    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(tasks_bp, url_prefix="/")
    app.register_blueprint(health_bp, url_prefix="/")

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        from app.models import User, Task
        db.create_all()
        if not testing:
            _seed_default_user()

    return app


def _seed_default_user():
    from app.models import User
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
