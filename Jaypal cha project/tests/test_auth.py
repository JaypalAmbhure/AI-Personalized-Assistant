from app.models import User

def test_user_registration(client, app):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'currency': '$',
        'monthly_income_target': '4000'
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.check_password('password123')
        assert user.currency == '$'

def test_duplicate_user_rejected(client, app):
    client.post('/register', data={
        'username': 'dupuser',
        'email': 'dup@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    # Logout so client is unauthenticated for the second attempt
    client.get('/logout', follow_redirects=True)

    # Second attempt with same username
    response = client.post('/register', data={
        'username': 'dupuser',
        'email': 'different@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'already taken' in response.data

def test_login_success_and_logout(client, app):
    with app.app_context():
        u = User(username='loginuser', email='login@example.com')
        u.set_password('secretpass')
        db = app.extensions['sqlalchemy']
        db.session.add(u)
        db.session.commit()

    # Valid Login
    res = client.post('/login', data={
        'identifier': 'loginuser',
        'password': 'secretpass'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome back' in res.data

    # Logout
    logout_res = client.get('/logout', follow_redirects=True)
    assert b'logged out safely' in logout_res.data

def test_login_invalid_password(client, app):
    with app.app_context():
        u = User(username='targetuser', email='target@example.com')
        u.set_password('correctpass')
        db = app.extensions['sqlalchemy']
        db.session.add(u)
        db.session.commit()

    res = client.post('/login', data={
        'identifier': 'targetuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid username/email or password' in res.data

def test_protected_routes_require_login(client):
    res = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in to access this page' in res.data
