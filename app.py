from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import random
import logging

app = Flask(__name__)
app.secret_key = 'llave_secreta'

# Enable logging to see the error message
# logging.basicConfig(level=logging.DEBUG)

client = MongoClient("mongodb://localhost:27017")
# CAMBIAR NOMBRE DE BASES DE DATOS SI ES NECESARIO
db = client["inventario_empresa"]


@app.route("/")  # INDEX
def index():
    collection = db["productos"]
    productos = collection.find()
    return render_template("index.html", productos=productos)


@app.route("/productos/<int:page>")  # Productos
def productos(page):
    collection = db["productos"]

    products_per_page = 12
    total_products = collection.count_documents({})

    productos = collection.find().skip(
        (page - 1) * products_per_page).limit(products_per_page)
    return render_template("productos.html", productos=productos, page=page, products_per_page=products_per_page, total_products=total_products)


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
    return render_template('form_new_producto.html', proveedores=proveedores_list, categorias=categorias_list)


@app.route('/select_producto_delete')  # PRE BORRAR PRODUCTO
def select_producto_delete():
    collection = db["productos"]

    productos = collection.find()
    query = request.args.get('q')
    if query:
        results = collection.find(
            {'title': {'$regex': query, '$options': 'i'}})
    else:
        results = []
    return render_template('select_producto_delete.html', query=query, results=results, productos=productos)


@app.route('/delete_producto/<int:id>')  # BORRAR PRODUCTO
def delete_producto(id):
    collection = db["productos"]
    collection.delete_one({"id": id})
    flash('Producto borrado con éxito!')
    return redirect(url_for("select_producto_delete"))


@app.route('/select_producto_update')  # PRE UPDATE PRODUCTO
def select_producto_update():
    collection = db["productos"]

    productos = collection.find()
    query = request.args.get('q')
    if query:
        results = collection.find(
            {'title': {'$regex': query, '$options': 'i'}})
    else:
        results = []
    return render_template('select_producto_update.html', query=query, results=results, productos=productos)


# UPDATE PRODUCTO
@app.route('/update_producto/<int:id>', methods=['GET', 'POST'])
def update_producto(id):

    productos = db["productos"]
    proveedores = db["proveedores"]
    categorias = db["categorias"]

    proveedores_list = proveedores.find()
    categorias_list = categorias.find()

    producto = productos.find_one({'id': id})

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        provider = request.form.get('provider')
        category = request.form.get('category')
        thumbnail = request.form.get('thumbnail')
        filter = {"id": id}
        update = {"$set": {'id': id, 'title': title, 'description': description, 'price': price,
                           'stock': stock, 'provider': provider, 'category': category, 'thumbnail': thumbnail}}
        productos.update_one(filter, update)
        flash('Producto actualizado con éxito!')
        return redirect(url_for('add_producto'))
    return render_template('form_update_producto.html', proveedores=proveedores_list, categorias=categorias_list, producto=producto)


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
