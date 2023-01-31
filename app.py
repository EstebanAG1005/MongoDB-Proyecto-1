from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import random
import logging

app = Flask(__name__)
app.secret_key = 'llave_secreta'

# Enable logging to see the error message
logging.basicConfig(level=logging.DEBUG)

client = MongoClient("mongodb://localhost:27017")
db = client["inventario_empresa"]


@app.route("/")  # INDEX
def index():
    collection = db["productos"]
    productos = collection.find()
    return render_template("index.html", productos=productos)


@app.route("/productos")  # Productos
def productos():
    collection = db["productos"]
    productos = collection.find()
    return render_template("productos.html", productos=productos)


@app.route("/categorias")  # Categorias
def categorias():
    collection = db["categorias"]
    categorias = collection.find()
    return render_template("categorias.html", categorias=categorias)


@app.route('/add_producto', methods=['GET', 'POST'])  # ADD PRODUCTOS
def add_producto():

    productos = db["productos"]
    proveedores = db["proveedores"]
    categorias = db["categorias"]

    proveedores_list = proveedores.find()
    categorias_list = categorias.find()

    random_id = random.randint(0, 100000000)

    while productos.find_one({'id': random_id}) is not None:
        random_id = random.randint(0, 100000000)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        provider = request.form.get('provider')
        category = request.form.get('category')
        thumbnail = request.form.get('thumbnail')
        inserts = {'id': random_id, 'title': title, 'description': description, 'price': price,
                   'stock': stock, 'provider': provider, 'category': category, 'thumbnail': thumbnail}
        productos.insert_one(inserts)
        flash('Producto añadido con éxito!')
        return redirect(url_for('add_producto'))
    return render_template('form_new_product.html', proveedores=proveedores_list, categorias=categorias_list)


@app.route('/search')  # SEARCH BAR
def search():
    collection = db["productos"]
    query = request.args.get('q')
    if query:
        results = collection.find(
            {'title': {'$regex': query, '$options': 'i'}})
    else:
        results = []
    return render_template('search_results.html', query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
