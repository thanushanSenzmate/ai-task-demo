import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        from app.models import User
        if not User.query.filter_by(username="admin").first():
            user = User(username="admin")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    return {}
