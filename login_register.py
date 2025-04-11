from models import db, User

def add_user(name, surname, city, login, password):
    user = User(name=name, surname=surname, city=city, login=login, password=password)
    db.session.add(user)
    db.session.commit()

def validate_user(login_input, password_input):
    return User.query.filter_by(login=login_input, password=password_input).first()