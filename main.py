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
    return redirect(url_for('index'))

@app.route('/electroguitars')
def electroguitars():
    return render_template('electroguitars.html')

@app.route('/pianos')
def pianos():
    return render_template('pianos.html')

if __name__ == "__main__":
    create_db(app) 
    app.run(debug=True)