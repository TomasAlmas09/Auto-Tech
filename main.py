from flask import Flask, render_template

app = Flask(__name__)

produtos = [
    {'id': 1, 'nome': 'Jantes Desportivas', 'preco': 300, 'descricao': "Descrição do Produto 1"},
    {'id': 2, 'nome': 'Spoiler Traseiro', 'preco': 150, 'descricao': "Descrição do Produto 2"},
    {'id': 3, 'nome': 'Coilovers', 'preco': 400, 'descricao': "Descrição do Produto 3"},
    {'id': 4, 'nome': 'Front Lip', 'preco': 100, 'descricao': "Descrição do Produto 4"},
    {'id': 5, 'nome': 'Grelha Frontal', 'preco': 250, 'descricao': "Descrição do Produto 5"}
]

@app.route('/')
def index():
    return render_template('index.html', name="Produtos automotivos", produtos=produtos)

@app.route('/perfil')
def perfil():
    return render_template('profile.html', name="Perfil")

@app.route('/carrinho')
def carrinho():
    return render_template('cart.html', name="Carrinho")

@app.route('/checkout')
def checkout():
    return render_template('checkout.html', name="Checkout")

@app.route('/login')
def login():
    return render_template('login.html', name="Login")

# Rota para visualizar detalhes do produto
@app.route('/produtos/<string:nome>')
def produto(nome):
    produto_encontrado = next((produto for produto in produtos if produto['nome'] == nome), None)
    if produto_encontrado is None:
        return render_template('404.html', name="Produto Não Encontrado"), 404
    return render_template('product-single.html', produto=produto_encontrado)

@app.route('/registo')
def registo():
    return render_template('registry.html', name="Registo")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', name="Not Found"), 404

if __name__ == '__main__':
    app.run(debug=True)
