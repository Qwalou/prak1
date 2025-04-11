from flask import session, redirect, url_for, request
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_items():
    cart_items = session.get('cart', [])
    
    items_summary = {}
    for item in cart_items:
        key = (item['name'], item['price'])
        if key in items_summary:
            items_summary[key]['quantity'] += 1
        else:
            items_summary[key] = {
                'name': item['name'],
                'price': item['price'],
                'quantity': 1
            }
    
    return list(items_summary.values())

def calculate_total(items):
    return sum(int(item['price']) * item['quantity'] for item in items)

def add_to_cart_handler():
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')

    if not product_name or not product_price:
        return redirect(url_for('pianos'))

    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append({
        'name': product_name, 
        'price': product_price
    })
    session.modified = True
    
    return redirect(request.referrer or url_for('pianos'))

def remove_from_cart_handler():
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')
    
    if not product_name or not product_price or 'cart' not in session:
        return redirect(url_for('cart'))
    
    session['cart'] = [
        item for item in session['cart'] 
        if item['name'] != product_name or item['price'] != product_price
    ]
    session.modified = True
    
    return redirect(url_for('cart'))

def increase_quantity_handler():
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')

    if not product_name or not product_price:
        return redirect(url_for('cart'))

    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append({
        'name': product_name, 
        'price': product_price
    })
    session.modified = True
    
    return redirect(url_for('cart'))

def decrease_quantity_handler():
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')
    
    if not product_name or not product_price or 'cart' not in session:
        return redirect(url_for('cart'))
    
    for i, item in enumerate(session['cart']):
        if item['name'] == product_name and item['price'] == product_price:
            session['cart'].pop(i)
            session.modified = True
            break
    
    return redirect(url_for('cart'))

def checkout_handler():
    session.pop('cart', None)
    session.modified = True
    return redirect(url_for('cart'))