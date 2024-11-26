from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')  

@app.route('/registry')
def registry():
    return render_template('registry.html') 

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
