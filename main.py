from flask import Flask, render_template, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


app = Flask(__name__)

# Configuração da chave secreta para formulários seguros e da URI do banco de dados
app.config['SECRET_KEY'] = 'hard to guess string'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Modelo de dados para o carrinho de compras
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  o
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  
    user = db.relationship('User', backref='cart')  
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  
    product = db.relationship('Product', backref='cart')  

    def __repr__(self):
        return f'<Cart {self.id}>'

# Modelo de dados para os produtos
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    nome = db.Column(db.String(128), unique=True)  
    descricao = db.Column(db.String(256))  
    preco = db.Column(db.Float)  
    imagem = db.Column(db.String(128))  

    def __repr__(self):
        return f'<Product {self.nome}>'

# Modelo de dados para os usuários
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    nome = db.Column(db.String(64), unique=True)  
    email = db.Column(db.String(64), unique=True)  
    senha = db.Column(db.String(128))  

    def __repr__(self):
        return f'<User {self.nome}>'

# Formulário para login do usuário
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])  
    password = PasswordField('Senha', validators=[DataRequired()])  
    submit = SubmitField('Entrar')  

# Formulário para registro de novos usuários
class RegistryForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    senha = PasswordField('Senha', validators=[DataRequired()]) 
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir.')])  
    submit = SubmitField('Registrar')  

# Rota principal do site, exibindo todos os produtos
@app.route('/')
def index():
    products = Product.query.all()  
    return render_template('index.html', products=products) 

# Rota para login de usuários
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() 
    if form.validate_on_submit():  
        email = form.email.data  
        password = form.password.data  
        user = User.query.filter_by(email=email).first() 

        if user and check_password_hash(user.senha, password):  
            session['user_id'] = user.id 
            flash(f'Bem-vindo, {email}', 'success')  
            return redirect(url_for('index'))  
        else:
            flash('Email ou senha inválidos', 'error')  

    return render_template('login.html', form=form)  

# Rota para registro de novos usuários
@app.route('/registry', methods=['GET', 'POST'])
def registry():
    form = RegistryForm()  
    if form.validate_on_submit(): 
        nome = form.nome.data  
        email = form.email.data  
        senha = generate_password_hash(form.senha.data)  

        user = User.query.filter_by(email=email).first() 
        if user:
            flash('Já existe uma conta com este email. Tente um email diferente.', 'error')  
            return redirect(url_for('registry'))  

        new_user = User(nome=nome, email=email, senha=senha)  
        db.session.add(new_user)  
        db.session.commit()  

        flash(f'Conta criada com sucesso para {nome}!', 'success')  
        return redirect(url_for('login'))  

    return render_template('registry.html', form=form)  

# Rota para visualizar um produto específico
@app.route('/product-single/<int:product_id>')
def product_single(product_id):
    product = Product.query.get_or_404(product_id)  
    return render_template('product-single.html', product=product)  

# Rota para exibir o perfil do usuário logado
@app.route('/profile')
def profile():
    user_id = session.get('user_id') 
    if not user_id:  
        flash('Você precisa estar logado para acessar o perfil', 'error')  
        return redirect(url_for('login'))  

    user = User.query.get(user_id)  
    return render_template('profile.html', user=user)  

# Rota para exibir o carrinho de compras do usuário logado
@app.route('/cart')
def cart():
    user_id = session.get('user_id')  
    if not user_id:  
        flash('Você precisa estar logado para acessar o carrinho', 'error')  
        return redirect(url_for('login'))  

    cart_items = Cart.query.filter_by(user_id=user_id).all()  
    return render_template('cart.html', cart_items=cart_items)  

# Rota para a página de checkout
@app.route('/checkout')
def checkout():
    return render_template('checkout.html') 

# Rota para tratar erros 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

# Iniciar a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)  
