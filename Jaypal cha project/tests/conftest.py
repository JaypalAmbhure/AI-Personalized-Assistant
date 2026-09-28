import pytest
from app import create_app
from app.models import db, User, Category

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(app, client):
    """Client with an authenticated user session."""
    with app.app_context():
        user = User(
            username='testuser',
            email='testuser@example.com',
            currency='$',
            monthly_income_target=5000.0,
            emergency_fund_months=6
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Log in through client
    client.post('/login', data={
        'identifier': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    return client
