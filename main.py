from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    senha = db.Column(db.String(12))

    def __repr__(self):
        return f'<User {self.nome}>'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegistryForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])  
    email = StringField('Email', validators=[DataRequired(), Email()])  
    senha = PasswordField('Senha', validators=[DataRequired()])  
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir.')]) 
    submit = SubmitField('Registrar')  




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    name = None
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, password):  
            flash(f'Bem-vindo, {email}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos', 'error')

    return render_template('login.html', form=form, name=name)

@app.route('/registry', methods=['GET', 'POST'])
def registry():
    form = RegistryForm()
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data
        
    user = User.query.filter_by(email=email).first() 
    if user:
            flash('Já existe uma conta com este email. Tente um email diferente.', 'erro')
            return redirect(url_for('registry'))

        
    new_user = User(nome=nome, email=email, senha=senha)
    db.session.add(new_user)  
    db.session.commit()  

    flash(f'Conta criada com sucesso para {nome}!', 'success')
    return redirect(url_for('login'))
    
    return render_template('registry.html', form=form) 

@app.route('/product-single')
def product_single():
    return render_template('product-single.html')  

@app.route('/profile')
def profile():
    return render_template('profile.html')  

@app.route('/cart')
def cart():
    return render_template('cart.html')  

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')  

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

if __name__ == "__main__":
    app.run(debug=True)
