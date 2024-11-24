import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(15), nullable=True)

    # Morada de residência
    rua = db.Column(db.String(128), nullable=True)
    numero = db.Column(db.String(10), nullable=True)
    cidade = db.Column(db.String(64), nullable=True)
    codigo_postal = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(64), nullable=True)

    # Morada de faturação
    rua_faturacao = db.Column(db.String(128), nullable=True)
    numero_faturacao = db.Column(db.String(10), nullable=True)
    cidade_faturacao = db.Column(db.String(64), nullable=True)
    codigo_postal_faturacao = db.Column(db.String(10), nullable=True)
    pais_faturacao = db.Column(db.String(64), nullable=True)


# Inicialização do banco de dados e inserção de dados iniciais
def init_db():
    with app.app_context():
        db.create_all()
        if Produto.query.count() == 0:
            produtos_iniciais = [
                Produto(nome='Jantes Desportivas', preco=300, descricao="Descrição do Produto 1", stock=25, rating=4),
                Produto(nome='Spoiler Traseiro', preco=150, descricao="Descrição do Produto 2", stock=6, rating=3),
                Produto(nome='Coilovers', preco=400, descricao="Descrição do Produto 3", stock=30, rating=5),
                Produto(nome='Front Lip', preco=100, descricao="Descrição do Produto 4", stock=10, rating=2),
                Produto(nome='Grelha Frontal', preco=250, descricao="Descrição do Produto 5", stock=50, rating=4),
            ]
            db.session.add_all(produtos_iniciais)
            db.session.commit()

# Inicializar banco de dados ao importar
init_db()

# Função para carregar o usuário para login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas
@app.route('/')
def index():
    produtos = Produto.query.all()
    return render_template('index.html', name="Produtos Automotivos",produtos=produtos, user = current_user)

@app.route('/produtos/<string:nome>')
def produto(nome):
    produto_encontrado = Produto.query.filter_by(nome=nome).first()
    if not produto_encontrado:
        return render_template('404.html', name="Produto Não Encontrado"), 404
    return render_template('product-single.html', produto=produto_encontrado, name=nome)

@app.route('/perfil')
@login_required
def perfil():
    return render_template('profile.html', name="Perfil", user = current_user)

@app.route('/carrinho')
@login_required
def carrinho():
    return render_template('cart.html', name="Carrinho", user = current_user)

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html', name="Checkout", user = current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Email ou senha inválidos", "danger")
    return render_template('login.html', name="Login", user = current_user)

@app.route('/registo', methods=['GET', 'POST'])
def registo():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar-senha']
        phone = request.form['phone']
        rua = request.form['rua']
        numero = request.form['numero']
        cidade = request.form['cidade']
        codigo_postal = request.form['codigo_postal']
        country = request.form['country']
        rua_faturacao = request.form['rua-faturacao']
        numero_faturacao = request.form['numero-faturacao']
        cidade_faturacao = request.form['cidade-faturacao']
        codigo_postal_faturacao = request.form['codigo-postal-faturacao']
        pais_faturacao = request.form['pais-faturacao']

        if senha != confirmar_senha:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for('registo'))

        if User.query.filter_by(email=email).first():
            flash("Email já registrado", "danger")
            return redirect(url_for('registo'))

        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        novo_usuario = User(
            nome=nome,
            email=email,
            senha=senha_hash,
            phone=phone,
            rua=rua,
            numero=numero,
            cidade=cidade,
            codigo_postal=codigo_postal,
            country=country,
            rua_faturacao=rua_faturacao,
            numero_faturacao=numero_faturacao,
            cidade_faturacao=cidade_faturacao,
            codigo_postal_faturacao=codigo_postal_faturacao,
            pais_faturacao=pais_faturacao
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro bem-sucedido! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('registry.html', name="Registo", user = current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index', user = current_user))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', name="Not Found", user = current_user), 404

# Ponto de entrada
if __name__ == '__main__':
    app.run(debug=True)
