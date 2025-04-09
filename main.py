from flask import Flask, render_template, request, redirect, url_for, session
from login_register import db, create_db, add_user, validate_user

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
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    
    # Группируем товары по имени и цене
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
    
    # Преобразуем в список и считаем общую сумму
    items_list = list(items_summary.values())
    total = sum(int(item['price']) * item['quantity'] for item in items_list)
    
    return render_template('cart.html', 
                         cart_items=items_list, 
                         total=total,
                         user=session.get('user'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return redirect(url_for('login'))  

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
    
    # Возвращаем на предыдущую страницу или на страницу пианино
    return redirect(request.referrer or url_for('pianos'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return redirect(url_for('login'))  

    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')
    
    if not product_name or not product_price or 'cart' not in session:
        return redirect(url_for('cart'))
    
    # Удаляем все экземпляры товара с указанными именем и ценой
    session['cart'] = [
        item for item in session['cart'] 
        if item['name'] != product_name or item['price'] != product_price
    ]
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/increase_quantity', methods=['POST'])
def increase_quantity():
    if 'user' not in session:
        return redirect(url_for('login'))  

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

@app.route('/decrease_quantity', methods=['POST'])
def decrease_quantity():
    if 'user' not in session:
        return redirect(url_for('login'))  

    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price')
    
    if not product_name or not product_price or 'cart' not in session:
        return redirect(url_for('cart'))
    
    # Находим первый подходящий товар и удаляем его
    for i, item in enumerate(session['cart']):
        if item['name'] == product_name and item['price'] == product_price:
            session['cart'].pop(i)
            session.modified = True
            break
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))  

    # Очищаем корзину после оформления
    session.pop('cart', None)
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/electroguitars')
def electroguitars():
    return render_template('electroguitars.html')

@app.route('/pianos')
def pianos():
    return render_template('pianos.html')

if __name__ == "__main__":
    create_db(app) 
    app.run(debug=True)