from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, render_templateC:\Users\Qutiaa\PycharmProjects\PythonProject

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.String(20), nullable=False)

# ---------------- CRUD API ----------------

# Получить все товары
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'quantity': p.quantity,
            'date_added': p.date_added
        })
    return jsonify(result), 200

# Получить товар по id
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'quantity': product.quantity,
        'date_added': product.date_added
    }), 200

# Добавить новый товар
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data or not all(k in data for k in ('name','category','price','quantity','date_added')):
        return jsonify({'error': 'Missing data'}), 400

    new_product = Product(
        name=data['name'],
        category=data['category'],
        price=data['price'],
        quantity=data['quantity'],
        date_added=data['date_added']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added', 'id': new_product.id}), 201

# Обновить товар
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    data = request.get_json()
    for field in ['name','category','price','quantity','date_added']:
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Product updated'}), 200

# Удалить товар
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

# ---------------- Главная страница ----------------
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
