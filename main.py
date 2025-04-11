from flask import Flask, render_template, request, redirect, url_for, session, abort, Response
from functools import wraps
from models import db, User, Product, Category
from login_register import add_user, validate_user, create_roles
from cart_handler import (login_required, get_cart_items, calculate_total,
                          add_to_cart_handler, remove_from_cart_handler,
                          increase_quantity_handler, decrease_quantity_handler,
                          checkout_handler)

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://HOME-PC\\SQLEXPRESS/db1?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_db(app):
    with app.app_context():
        db.create_all()
        create_roles()

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != required_role:
                abort(403)  
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if session.get('role') == 'Продавец':
        return redirect(url_for('add_product'))
    return render_template('index.html', user=session.get('user'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/add_user', methods=['POST'])
def create_account():
    if request.method == 'POST':
        name = request.form["name"]
        surname = request.form["surname"]
        city = request.form["city"]
        login = request.form["login"]
        password = request.form["pass"]
        add_user(name, surname, city, login, password)
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        login_input = request.form['login']
        password_input = request.form['pass']
        role_input = request.form['role']
        user = validate_user(login_input, password_input)
        if user:
            session['user'] = user.name
            session['role'] = role_input

            if role_input == 'Продавец':
                return redirect(url_for('add_product'))
            else:
                return redirect(url_for('index'))
        else:
            error = "Неверный логин или пароль"  
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)  
    session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
@role_required('Покупатель')
def cart():
    items_list = get_cart_items()
    total = calculate_total(items_list)
    return render_template('cart.html', 
                         cart_items=items_list, 
                         total=total,
                         user=session.get('user'))

@app.route('/add_to_cart', methods=['POST'])
@login_required
@role_required('Покупатель')
def add_to_cart():
    return add_to_cart_handler()

@app.route('/remove_from_cart', methods=['POST'])
@login_required
@role_required('Покупатель')
def remove_from_cart():
    return remove_from_cart_handler()

@app.route('/increase_quantity', methods=['POST'])
@login_required
@role_required('Покупатель')
def increase_quantity():
    return increase_quantity_handler()

@app.route('/decrease_quantity', methods=['POST'])
@login_required
@role_required('Покупатель')
def decrease_quantity():
    return decrease_quantity_handler()

@app.route('/checkout', methods=['POST'])
@login_required
@role_required('Покупатель')
def checkout():
    return checkout_handler()

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@role_required('Продавец')
def add_product():
    if 'user' not in session:
        return redirect(url_for('register'))

    if request.method == 'POST':
        brand = request.form["brand"]
        price = request.form["price"]
        category_name = request.form["category"]
        photo = request.files.get("photo")

        photo_data = None
        if photo and photo.filename:
            photo_data = photo.read()

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        user = User.query.filter_by(name=session['user']).first() 
        if not user:
            return "Пользователь не найден!", 400

        new_product = Product(brand=brand, price=price, photo=photo_data,  category_id=category.id, user_id=user.id) 
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('show_products', category_name=category_name))
    return render_template('add_product.html')

@app.route('/product_image/<int:product_id>')
def product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.photo:
        return "", 404
    return Response(product.photo, mimetype='image/jpeg')

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required('Продавец')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    user = User.query.filter_by(name=session['user']).first()
    if not user or product.user_id != user.id:
        abort(403)
    
    category_name = product.category.name
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('show_products', category_name=category_name))

def get_route_for_category(category_name):
    return url_for('show_products', category_name=category_name)

@app.route('/products/<category_name>')
def show_products(category_name):
    category = Category.query.filter_by(name=category_name).first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('products.html', products=products, category_name=category_name, user=session.get('user'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    # Ищем товары, в названии которых есть поисковый запрос (без учета регистра)
    products = Product.query.filter(Product.brand.ilike(f'%{query}%')).all()
    
    # Группируем товары по категориям для удобного отображения
    categories = {}
    for product in products:
        if product.category.name not in categories:
            categories[product.category.name] = []
        categories[product.category.name].append(product)
    
    return render_template('search_results.html', 
                         query=query,
                         categories=categories,
                         user=session.get('user'))

if __name__ == "__main__":
    create_db(app)
    app.run(debug=True)
    