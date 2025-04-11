from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50))
    city = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(12), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    products = db.relationship('Product', backref='user', lazy=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)  
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    brand = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    photo = db.Column(LargeBinary)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)