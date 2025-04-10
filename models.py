from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50))
    city = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(12), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(20), nullable=False) 
    price = db.Column(db.Integer, nullable=False)    
    category = db.Column(db.String(50), nullable=False)  

def create_db(app):
    with app.app_context():
        db.create_all()