import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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
    return render_template('index.html', name="Produtos Automotivos",produtos=produtos)

@app.route('/produtos/<string:nome>')
def produto(nome):
    produto_encontrado = Produto.query.filter_by(nome=nome).first()
    if not produto_encontrado:
        return render_template('404.html', name="Produto Não Encontrado"), 404
    return render_template('product-single.html', produto=produto_encontrado, name=nome)

@app.route('/perfil')
@login_required
def perfil():
    return render_template('profile.html', name="Perfil", ola = current_user)

@app.route('/carrinho')
@login_required
def carrinho():
    return render_template('cart.html', name="Carrinho")

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html', name="Checkout")

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
    return render_template('login.html', name="Login")

@app.route('/registo', methods=['GET', 'POST'])
def registo():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar-senha']

        if senha != confirmar_senha:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for('registo'))

        if User.query.filter_by(email=email).first():
            flash("Email já registrado", "danger")
            return redirect(url_for('registo'))

        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        novo_usuario = User(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro bem-sucedido! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('registry.html', name="Registo")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', name="Not Found"), 404

# Ponto de entrada
if __name__ == '__main__':
    app.run(debug=True)
