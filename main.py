from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    name = None
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('login.html', form=form, name=name)

@app.route('/registry', methods=['GET', 'POST'])
def registry():
    form = RegistryForm()
    
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data
        
        flash(f'Conta criada com sucesso para {nome}!', 'success')
        
       
        return render_template('registry.html')
    
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
