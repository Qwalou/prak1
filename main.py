from flask import Flask, render_template, request, redirect, url_for, session, Response
from models import db, create_db, User, Product, Category
from login_register import add_user, validate_user
from cart_handler import (login_required, get_cart_items, calculate_total,
                          add_to_cart_handler, remove_from_cart_handler,
                          increase_quantity_handler, decrease_quantity_handler,
                          checkout_handler)

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://HOME-PC\\SQLEXPRESS/db1?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

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
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        login_input = request.form['login']
        password_input = request.form['pass']
        user = validate_user(login_input, password_input)
        if user:
            session['user'] = user.name 
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
def cart():
    items_list = get_cart_items()
    total = calculate_total(items_list)
    return render_template('cart.html', 
                         cart_items=items_list, 
                         total=total,
                         user=session.get('user'))

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    return add_to_cart_handler()

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    return remove_from_cart_handler()

@app.route('/increase_quantity', methods=['POST'])
@login_required
def increase_quantity():
    return increase_quantity_handler()

@app.route('/decrease_quantity', methods=['POST'])
@login_required
def decrease_quantity():
    return decrease_quantity_handler()

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    return checkout_handler()

def get_route_for_category(category_name):
    category_mapping = {
        "Электрогитары": "electroguitars",
        "Акустические гитары": "acoustic_guitars",
        "Классические гитары": "classical_guitars",
        "Пианино": "pianos",
        "Электронные ударные": "electronic_drums",
        "Акустические ударные": "acoustic_drums",
    }
    return category_mapping.get(category_name, "index")  

@app.route('/add_product', methods=['GET', 'POST'])
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

        route_name = get_route_for_category(category_name)
        return redirect(url_for(route_name))

    return render_template('product_form.html')

@app.route('/product_image/<int:product_id>')
def product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.photo:
        return "", 404
    return Response(product.photo, mimetype='image/jpeg')

@app.route('/electroguitars')
def electroguitars():
    category = Category.query.filter_by(name="Электрогитары").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('electroguitars.html', products=products, user=session.get('user'))

@app.route('/acoustic_guitars')
def acoustic_guitars():
    category = Category.query.filter_by(name="Акустические гитары").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('acoustic_guitars.html', products=products, user=session.get('user'))

@app.route('/classical_guitars')
def classical_guitars():
    category = Category.query.filter_by(name="Классические гитары").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('classical_guitars.html', products=products, user=session.get('user'))

@app.route('/pianos')
def pianos():
    category = Category.query.filter_by(name="Пианино").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('pianos.html', products=products, user=session.get('user'))

@app.route('/electronic_drums')
def electronic_drums():
    category = Category.query.filter_by(name="Электронные ударные").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('electronic_drums.html', products=products, user=session.get('user'))

@app.route('/acoustic_drums')
def acoustic_drums():
    category = Category.query.filter_by(name="Акустические ударные").first()
    if category:
        products = Product.query.filter_by(category_id=category.id).all()
    else:
        products = []
    return render_template('acoustic_drums.html', products=products, user=session.get('user'))

if __name__ == "__main__":
    create_db(app)
    app.run(debug=True)