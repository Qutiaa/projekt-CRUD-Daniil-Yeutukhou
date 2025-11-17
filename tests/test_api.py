import pytest
from flask_crud_shop import app, db, Product, Admin

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = Admin(username='admin')
        admin.set_password('1234')
        db.session.add(admin)
        db.session.commit()

    with app.test_client() as client:
        # логинимся для всех тестов
        response = client.post('/login', data={
            'username': 'admin',
            'password': '1234'
        }, follow_redirects=True)  # follow_redirects=True сохраняет сессию
        assert response.status_code == 200
        yield client

def test_add_product(client):
    response = client.post('/products', json={
        'name': 'Test Product',
        'category': 'Test Category',
        'price': 10.5,
        'quantity': 5,
        'date_added': '2025-01-01'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data

def test_update_product(client):
    with app.app_context():
        product = Product(name='Old Name', category='Old Cat', price=5, quantity=2, date_added='2025-01-01')
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.put(f'/products/{product_id}', json={
        'name': 'New Name',
        'category': 'New Cat',
        'price': 15.0,
        'quantity': 10,
        'date_added': '2025-01-01'
    })
    assert response.status_code == 200

def test_delete_product(client):
    with app.app_context():
        product = Product(name='Delete Me', category='Cat', price=1, quantity=1, date_added='2025-01-01')
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.delete(f'/products/{product_id}')
    assert response.status_code == 200
