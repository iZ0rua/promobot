from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Promo, init_db
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    
    # Инициализация БД
    init_db(app)
    
    # Настройка Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ========== ПРИ ЗАПУСКЕ СОЗДАЕМ ГЛАВНОГО АДМИНА ==========
    with app.app_context():
        db.create_all()
        
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Проверяем, есть ли такой админ. Если нет — создаем.
        existing_admin = User.query.filter_by(username=admin_username).first()
        if not existing_admin:
            new_admin = User(username=admin_username)
            new_admin.set_password(admin_password)
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ Создан главный админ: {admin_username}")
    
    # ========== РОУТЫ ==========
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            # Проверяем пароль
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            flash('Неверное имя пользователя или пароль', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        promos = Promo.query.order_by(Promo.created_at.desc()).all()
        return render_template('dashboard.html', promos=promos)
    
    @app.route('/promo/add', methods=['GET', 'POST'])
    @login_required
    def add_promo():
        if request.method == 'POST':
            promo = Promo(
                keyword=request.form.get('keyword').lower().strip(),
                title=request.form.get('title'),
                promo_code=request.form.get('promo_code'),
                conditions=request.form.get('conditions'),
                link=request.form.get('link'),
                emoji=request.form.get('emoji', ''),
                author_id=current_user.id
            )
            
            try:
                db.session.add(promo)
                db.session.commit()
                flash('Промокод добавлен!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка: промокод с таким ключевым словом уже существует', 'error')
        
        return render_template('promo_form.html', promo=None, action='add')
    
    @app.route('/promo/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_promo(id):
        promo = Promo.query.get_or_404(id)
        
        if request.method == 'POST':
            promo.keyword = request.form.get('keyword').lower().strip()
            promo.title = request.form.get('title')
            promo.promo_code = request.form.get('promo_code')
            promo.conditions = request.form.get('conditions')
            promo.link = request.form.get('link')
            promo.emoji = request.form.get('emoji', '')
            
            try:
                db.session.commit()
                flash('Промокод обновлён!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при обновлении', 'error')
        
        return render_template('promo_form.html', promo=promo, action='edit')
    
    @app.route('/promo/delete/<int:id>')
    @login_required
    def delete_promo(id):
        promo = Promo.query.get_or_404(id)
        db.session.delete(promo)
        db.session.commit()
        flash('Промокод удалён', 'success')
        return redirect(url_for('dashboard'))
    
    # ========== API ДЛЯ БОТА ==========
    
    @app.route('/api/promo/<keyword>')
    def get_promo(keyword):
        promo = Promo.query.filter_by(keyword=keyword.lower()).first()
        if promo:
            return jsonify(promo.to_dict())
        return jsonify({'error': 'not found'}), 404
    
    @app.route('/api/promos')
    def get_all_promos():
        promos = Promo.query.all()
        return jsonify([p.to_dict() for p in promos])
    
    return app