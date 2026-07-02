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
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    db.init_app(app)

from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    promos = db.relationship('Promo', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# 🔹 НОВАЯ таблица для множественных ключей
class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False, index=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promos.id'), nullable=False)
    promo = db.relationship('Promo', backref='keywords_list', lazy=True)

class Promo(db.Model):
    __tablename__ = 'promos'
    id = db.Column(db.Integer, primary_key=True)
    
    # 🔹 СТАРОЕ поле оставляем (nullable=True), чтобы старые данные не сломались
    keyword = db.Column(db.String(100), nullable=True, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    promo_code = db.Column(db.String(100), nullable=False)
    conditions = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    emoji = db.Column(db.String(10), default='🎁')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        # Собираем все ключи: новые + старые (для обратной совместимости)
        keys = [k.keyword for k in self.keywords_list]
        if self.keyword and self.keyword not in keys:
            keys.append(self.keyword)
            
        return {
            'id': self.id,
            'title': self.title,
            'promo': self.promo_code,
            'conditions': self.conditions,
            'link': self.link,
            'emoji': self.emoji,
            'keywords': keys  # ← единый список всех ключевых слов
        }