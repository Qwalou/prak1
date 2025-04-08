from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50))
    city = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(12), nullable=False)

def create_db(app):
    with app.app_context():
        db.create_all()

def add_user(name, surname, city, login, password):
    user = User(name=name, surname=surname, city=city, login=login, password=password)
    db.session.add(user)
    db.session.commit()

def validate_user(login_input, password_input):
    return User.query.filter_by(login=login_input, password=password_input).first()