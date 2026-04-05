from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def init_db(app):
    """Инициализация базы данных"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///promobot.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

from flask_login import UserMixin  # ← Добавь этот импорт в начало файла

class User(db.Model, UserMixin):  # ← Добавь , UserMixin
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # ← Убедись, что 256!
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    promos = db.relationship('Promo', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Promo(db.Model):
    """Модель промокода"""
    __tablename__ = 'promos'
    
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    promo_code = db.Column(db.String(100), nullable=False)
    conditions = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    emoji = db.Column(db.String(10), default='🎁')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'keyword': self.keyword,
            'title': self.title,
            'promo': self.promo_code,
            'conditions': self.conditions,
            'link': self.link,
            'emoji': self.emoji
        }