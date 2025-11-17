from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # для сессий

db_path = os.path.join(os.path.dirname(__file__), 'products.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.String(20), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# -------------------- INIT DATABASE --------------------
with app.app_context():
    db.create_all()
    # Создаем начального админа, если его нет
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('1234')  # безопасно хешируется
        db.session.add(admin)
        db.session.commit()

# -------------------- LOGIN --------------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["user"] = username
            return redirect(url_for("warehouse"))
        else:
            error = "Niepoprawny login lub hasło"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------- VALIDATION --------------------
def validate_product(data):
    errors = []

    if not data.get('name') or len(data['name']) < 3 or len(data['name']) > 50:
        errors.append({'field': 'name', 'code': 'INVALID_LENGTH', 'message': 'Nazwa musi miec 3-50 znakow'})
    if not data.get('category'):
        errors.append({'field': 'category', 'code': 'REQUIRED', 'message': 'Kategoria jest wymagana'})
    if 'price' not in data or type(data['price']) not in [int, float] or data['price'] <= 0:
        errors.append({'field': 'price', 'code': 'INVALID_VALUE', 'message': 'Cena musi byc wieksza niz 0'})
    if 'quantity' not in data or type(data['quantity']) is not int or data['quantity'] <= 0:
        errors.append({'field': 'quantity', 'code': 'INVALID_VALUE', 'message': 'Ilosc musi byc wieksza niz 0'})
    if 'date_added' in data:
        try:
            d = date.fromisoformat(data['date_added'])
            if d > date.today():
                errors.append({'field': 'date_added', 'code': 'INVALID_DATE', 'message': 'Data nie moze byc w przyszlosci'})
        except:
            errors.append({'field': 'date_added', 'code': 'INVALID_FORMAT', 'message': 'Niepoprawny format daty'})
    return errors

# -------------------- API --------------------
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

@app.route('/products', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    if not data or not all(k in data for k in ('name','category','price','quantity','date_added')):
        return jsonify({'status': 400, 'error': 'Bad Request', 'fieldErrors': [{'field': 'general','code':'MISSING_DATA','message':'Нет данных'}]}), 400

    errors = validate_product(data)
    if errors:
        return jsonify({'status': 400, 'error': 'Bad Request', 'fieldErrors': errors}), 400

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

@app.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    errors = validate_product(data)
    if errors:
        return jsonify({'status': 400, 'error': 'Bad Request', 'fieldErrors': errors}), 400

    for field in ['name','category','price','quantity','date_added']:
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Product updated'}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

# -------------------- HTML --------------------
@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/warehouse')
@login_required
def warehouse():
    products = Product.query.all()
    return render_template('warehouse.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
