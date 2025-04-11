from models import db, User, Role

def add_user(name, surname, city, login, password):
    user = User(name=name, surname=surname, city=city, login=login, password=password)
    db.session.add(user)
    db.session.commit()

def create_roles():
    roles = ['Покупатель', 'Продавец']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()

def validate_user(login_input, password_input):
    return User.query.filter_by(login=login_input, password=password_input).first()