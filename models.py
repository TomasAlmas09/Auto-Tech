import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configs principais
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Diretório para upload das imagens

#  iniciar extensoes
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Tabelas
class Produto(db.Model):
    __tablename__ = 'produtos'  
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    rua = db.Column(db.String(128), nullable=True)
    numero = db.Column(db.String(10), nullable=True)
    cidade = db.Column(db.String(64), nullable=True)
    codigo_postal = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(64), nullable=True)
    rua_faturacao = db.Column(db.String(128), nullable=True)
    numero_faturacao = db.Column(db.String(10), nullable=True)
    cidade_faturacao = db.Column(db.String(64), nullable=True)
    codigo_postal_faturacao = db.Column(db.String(10), nullable=True)
    pais_faturacao = db.Column(db.String(64), nullable=True)
    imagem = db.Column(db.String(200), nullable=True)

class Cart(db.Model):
    __tablename__ = 'carts'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  
    product_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)  
    quantity = db.Column(db.Integer, default=1, nullable=True)

    # relacionar tabelas
    user = db.relationship('User', backref='cart_items')
    produto = db.relationship('Produto', backref='cart_items') 


# iniciar a base de dados com os produtos iniciais
def init_db():
    with app.app_context():
        db.create_all()
        if Produto.query.count() == 0:
            produtos_iniciais = [
                Produto(
                    nome='Jantes Desportivas', 
                    preco=300, 
                    descricao="Conjunto de jantes desportivas de alta performance, fabricadas em liga leve para maior durabilidade e estilo.", 
                    stock=25, 
                    rating=4
                ),
                Produto(
                    nome='Spoiler Traseiro', 
                    preco=150, 
                    descricao="Spoiler traseiro aerodinâmico que melhora a estabilidade em alta velocidade, adicionando um toque esportivo ao seu veículo.", 
                    stock=6, 
                    rating=3
                ),
                Produto(
                    nome='Coilovers', 
                    preco=400, 
                    descricao="Sistema de suspensão ajustável que permite customizar a altura e rigidez, ideal para entusiastas de performance.", 
                    stock=30, 
                    rating=5
                ),
                Produto(
                    nome='Front Lip', 
                    preco=100, 
                    descricao="Acessório de acabamento frontal que melhora o fluxo de ar e confere uma aparência agressiva ao veículo.", 
                    stock=10, 
                    rating=2
                ),
                Produto(
                    nome='Grelha Frontal', 
                    preco=250, 
                    descricao="Grelha frontal de design exclusivo, fabricada em materiais resistentes para combinar estilo e funcionalidade.", 
                    stock=50, 
                    rating=4
                ),
            ]
            db.session.add_all(produtos_iniciais)
            db.session.commit()

init_db()

# Gerenciar login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))