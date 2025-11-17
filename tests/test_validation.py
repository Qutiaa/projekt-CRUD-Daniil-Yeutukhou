import pytest
from flask_crud_shop import validate_product
from datetime import date, timedelta

def test_valid_product():
    data = {
        'name': 'Produkt A',
        'category': 'Kategoria',
        'price': 10.5,
        'quantity': 5,
        'date_added': str(date.today())
    }
    errors = validate_product(data)
    assert errors == []

def test_invalid_name():
    data = {'name':'AB', 'category':'cat','price':1,'quantity':1,'date_added':str(date.today())}
    errors = validate_product(data)
    assert any(e['field']=='name' for e in errors)

def test_invalid_price_quantity():
    data = {'name':'Produkt','category':'cat','price':0,'quantity':0,'date_added':str(date.today())}
    errors = validate_product(data)
    assert any(e['field']=='price' for e in errors)
    assert any(e['field']=='quantity' for e in errors)

def test_future_date():
    future = date.today() + timedelta(days=1)
    data = {'name':'Produkt','category':'cat','price':1,'quantity':1,'date_added':str(future)}
    errors = validate_product(data)
    assert any(e['field']=='date_added' for e in errors)
