import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from models import *

def paises():

    paises_por_continente = {
        "África": [
            "África do Sul", "Angola", "Argélia", "Cabo Verde", "Egito", 
            "Marrocos", "Moçambique", "Nigéria", "Tunísia", "Zâmbia"
        ],
        "América do Norte": [
            "Canadá", "Estados Unidos", "México", "Cuba", "Honduras"
        ],
        "América do Sul": [
            "Argentina", "Brasil", "Chile", "Colômbia", "Peru", 
            "Uruguai", "Venezuela"
        ],
        "Ásia": [
            "Arábia Saudita", "China", "Índia", "Indonésia", "Japão", 
            "Tailândia", "Turquia", "Vietnã"
        ],
        "Europa": [
            "Alemanha", "Espanha", "França", "Itália", "Portugal", 
            "Reino Unido", "Rússia", "Suíça"
        ],
        "Oceania": [
            "Austrália", "Fiji", "Nova Zelândia", "Papua Nova Guiné"
        ]
    }
    return(paises_por_continente)

# Rotas
@app.route('/')
def index():
    produtos = Produto.query.all()
    return render_template('index.html', name="Produtos Automotivos", produtos=produtos, user=current_user)

@app.route('/produtos/<string:nome>')
def produto(nome):
    produto_encontrado = Produto.query.filter_by(nome=nome).first()
    if not produto_encontrado:
        return render_template('404.html', name="Produto Não Encontrado"), 404
    return render_template('product-single.html', produto=produto_encontrado, name=nome, user=current_user)

@app.route('/perfil')
@login_required
def perfil():

    return render_template('profile.html', name="Perfil", user=current_user, paises_por_continente=paises())

@app.route('/carrinho')
@login_required
def carrinho():
    # Obtém os itens do carrinho para o usuário logado
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    # Calcula o total do carrinho
    total = sum(item.produto.preco * item.quantity for item in cart_items)

    # Renderiza o template com os dados necessários
    return render_template(
        'cart.html', 
        name="Carrinho", 
        user=current_user, 
        cart_items=cart_items, 
        total=total
    )

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))  # Valor padrão de 1, caso o campo não seja enviado corretamente

    # Logando o ID recebido para depuração
    if not product_id:
        app.logger.error("Erro ao adicionar ao carrinho: ID do produto não recebido ou inválido.")
        flash("ID do produto inválido.", "error")
        return redirect(request.referrer)

    # Consultando o produto pelo ID com Session.get()
    from sqlalchemy.orm import Session
    with Session(db.engine) as session:
        product = session.get(Produto, product_id)
        if not product:
            app.logger.error(f"Erro ao adicionar ao carrinho: Produto com ID {product_id} não encontrado.")
            flash("Produto inválido.", "error")
            return redirect(request.referrer)

    # Verificando se a quantidade solicitada é válida
    if quantity > product.stock:
        flash("Quantidade solicitada excede o estoque disponível.", "error")
        return redirect(request.referrer)

    # Verificando se o produto já está no carrinho do usuário
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity  # Aumenta a quantidade no carrinho
        flash(f"Quantidade aumentada no carrinho: {cart_item.quantity}.", "success")
    else:
        new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
        flash("Produto adicionado ao carrinho.", "success")

    # Commitando alterações
    db.session.commit()
    return redirect(url_for('carrinho'))


@app.route('/checkout')
@login_required
def checkout(): 
    return render_template('checkout.html', name="Checkout", user=current_user)

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
    return render_template('login.html', name="Login", user=current_user)

@app.route('/registo', methods=['GET', 'POST'])
def registo():

    if request.method == 'POST':
        # Dados do formulário
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
        
        # Processar imagem
        imagem_file = request.files['imagem']
        imagem_nome = secure_filename(imagem_file.filename) if imagem_file else None
        if imagem_file:
            imagem_file.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_nome))

        # Checar se "mesma-morada" está marcado
        if 'mesma-morada' in request.form:
            rua_faturacao, numero_faturacao = rua, numero
            cidade_faturacao, codigo_postal_faturacao, pais_faturacao = cidade, codigo_postal, country
        else:
            rua_faturacao = request.form['rua-faturacao']
            numero_faturacao = request.form['numero-faturacao']
            cidade_faturacao = request.form['cidade-faturacao']
            codigo_postal_faturacao = request.form['codigo-postal-faturacao']
            pais_faturacao = request.form['pais-faturacao']

        # Validar senha
        if senha != confirmar_senha:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for('registo'))

        # Validar email único
        if User.query.filter_by(email=email).first():
            flash("Email já registrado", "danger")
            return redirect(url_for('registo'))

        # Criar novo usuário
        novo_usuario = User(
            nome=nome, email=email, senha=generate_password_hash(senha), phone=phone,
            rua=rua, numero=numero, cidade=cidade, codigo_postal=codigo_postal, country=country,
            rua_faturacao=rua_faturacao, numero_faturacao=numero_faturacao,
            cidade_faturacao=cidade_faturacao, codigo_postal_faturacao=codigo_postal_faturacao,
            pais_faturacao=pais_faturacao, imagem=imagem_nome
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro bem-sucedido! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('registry.html', name="Registo", user=current_user, paises_por_continente=paises())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', name="Not Found", user=current_user), 404

# Executar o aplicativo
if __name__ == '__main__':
    app.run(debug=True)