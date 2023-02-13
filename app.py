from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
import random
import logging
import urllib.parse
import pymongo
import plotly.express as px
import pandas as pd


app = Flask(__name__)
app.secret_key = "llave_secreta"

# Enable logging to see the error message
# logging.basicConfig(level=logging.DEBUG)
username = urllib.parse.quote_plus("Proyecto1")
password = urllib.parse.quote_plus("Proyecto1_02")

client = MongoClient(
    f"mongodb+srv://{username}:{password}@cluster1.6bukxn9.mongodb.net/test",
    socketTimeoutMS=30000,
)

try:
    # Checquear la conexion a la base de datos
    print(client.list_database_names())
except Exception as e:
    print("Error connecting to the database:", e)

db = client["inventario_empresa"]


@app.route("/")  # INDEX
def index():
    prods = db["productos"]
    categorias = db["categorias"]
    proveedores = db["proveedores"]
    productos = prods.find()
    productos_sorted = prods.find().sort("price", -1)
    productos_stock = prods.find().sort("stock", -1)

    # Realizar la agregación
    pipeline = [
        # Agrupar los productos por categoría y calcular el número de productos en cada categoría
        {"$group": {"_id": "$category", "num_products": {"$sum": 1}}},
        # Ordenar los resultados por número de productos en cada categoría
        {"$sort": {"num_products": -1}},
        # Limitar los resultados a las tres categorías con más productos
        {"$limit": 3},
    ]

    top_categories = prods.aggregate(pipeline)

    return render_template(
        "index.html",
        productos=productos,
        productos_sorted=productos_sorted,
        productos_stock=productos_stock,
        top_categories=top_categories,
    )


@app.route("/productos/<int:page>")  # Productos
def productos(page):
    collection = db["productos"]

    products_per_page = 12
    total_products = collection.count_documents({})

    productos = (
        collection.find().skip((page - 1) * products_per_page).limit(products_per_page)
    )
    return render_template(
        "productos.html",
        productos=productos,
        page=page,
        products_per_page=products_per_page,
        total_products=total_products,
    )


@app.route("/categorias")  # Categorias
def categorias():
    collection = db["categorias"]
    categorias = collection.find()
    return render_template("categorias.html", categorias=categorias)


@app.route("/category/<category_name>")  # Categoria singular
def category_page(category_name):
    collection = db["productos"]
    productos = collection.find({"category": category_name})

    pipeline = [
        {"$match": {"category": category_name}},
        {"$group": {"_id": "$category", "average_price": {"$avg": "$price"}}},
    ]

    avg_price = list(collection.aggregate(pipeline))

    return render_template(
        "category_single.html",
        productos=productos,
        category_name=category_name,
        avg_price=avg_price[0]["average_price"],
    )


@app.route("/proveedores")  # Proveedores
def proveedores():
    collection = db["proveedores"]
    proveedores = collection.find()

    return render_template("proveedores.html", proveedores=proveedores)


@app.route("/add_producto", methods=["GET", "POST"])  # ADD PRODUCTOS
def add_producto():

    productos = db["productos"]
    proveedores = db["proveedores"]
    categorias = db["categorias"]

    proveedores_list = proveedores.find()
    categorias_list = categorias.find()

    random_id = random.randint(0, 100000000)

    while productos.find_one({"id": random_id}) is not None:
        random_id = random.randint(0, 100000000)

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        stock = request.form.get("stock")
        provider = request.form.get("provider")
        category = request.form.get("category")
        thumbnail = request.form.get("thumbnail")
        inserts = {
            "id": random_id,
            "title": title,
            "description": description,
            "price": price,
            "stock": stock,
            "provider": provider,
            "category": category,
            "thumbnail": thumbnail,
        }
        productos.insert_one(inserts)
        flash("Producto añadido con éxito!")
        return redirect(url_for("add_producto"))
    return render_template(
        "form_new_producto.html",
        proveedores=proveedores_list,
        categorias=categorias_list,
    )


@app.route("/select_producto_update")  # PRE UPDATE PRODUCTO
def select_producto_update():
    collection = db["productos"]

    productos = collection.find()
    query = request.args.get("q")
    if query:
        results = collection.find({"title": {"$regex": query, "$options": "i"}})
    else:
        results = []
    return render_template(
        "select_producto_update.html", query=query, results=results, productos=productos
    )


# UPDATE PRODUCTO
@app.route("/update_producto/<int:id>", methods=["GET", "POST"])
def update_producto(id):

    productos = db["productos"]
    proveedores = db["proveedores"]
    categorias = db["categorias"]

    proveedores_list = proveedores.find()
    categorias_list = categorias.find()

    producto = productos.find_one({"id": id})

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = int(request.form.get("price"))
        stock = int(request.form.get("stock"))
        provider = request.form.get("provider")
        category = request.form.get("category")
        thumbnail = request.form.get("thumbnail")
        filter = {"id": id}
        update = {
            "$set": {
                "id": id,
                "title": title,
                "description": description,
                "price": price,
                "stock": stock,
                "provider": provider,
                "category": category,
                "thumbnail": thumbnail,
            }
        }
        productos.update_one(filter, update)
        flash("Producto actualizado con éxito!")
    return render_template(
        "form_update_producto.html",
        proveedores=proveedores_list,
        categorias=categorias_list,
        producto=producto,
    )


@app.route("/select_producto_delete")  # PRE BORRAR PRODUCTO
def select_producto_delete():
    collection = db["productos"]

    productos = collection.find()
    query = request.args.get("q")
    if query:
        results = collection.find({"title": {"$regex": query, "$options": "i"}})
    else:
        results = []
    return render_template(
        "select_producto_delete.html", query=query, results=results, productos=productos
    )


@app.route("/delete_producto/<int:id>")  # BORRAR PRODUCTO
def delete_producto(id):
    collection = db["productos"]
    collection.delete_one({"id": id})
    flash("Producto borrado con éxito!")
    return redirect(url_for("select_producto_delete"))


@app.route("/add_category", methods=["GET", "POST"])  # ADD CATEGORIAS
def add_category():

    categorias = db["categorias"]

    random_id = random.randint(0, 100000000)

    while categorias.find_one({"id": random_id}) is not None:
        random_id = random.randint(0, 100000000)

    if request.method == "POST":
        title = request.form.get("title")
        inserts = {"id": random_id, "category_name": title}
        categorias.insert_one(inserts)
        flash("Categoría añadida con éxito!")
        return redirect(url_for("add_category"))
    return render_template("form_new_category.html")


@app.route("/select_category_update")  # PRE UPDATE CATEGORIA
def select_category_update():
    collection = db["categorias"]
    categorias = collection.find()
    return render_template("select_category_update.html", categorias=categorias)


# UPDATE CATEGORIAS
@app.route("/update_category/<int:id>", methods=["GET", "POST"])
def update_category(id):

    categorias = db["categorias"]
    productos = db["productos"]

    categoria = categorias.find_one({"id": id})

    if request.method == "POST":
        title = request.form.get("title")
        filter = {"id": id}
        update = {"$set": {"id": id, "category_name": title}}
        categorias.update_one(filter, update)
        flash("Categoría actualizada con éxito!")
        filter = {"category": categoria["category_name"]}
        update = {"$set": {"category": title}}
        productos.update_many(filter, update)
        flash("Prodcutos actualizados a la nueva categoría con éxito!")

    return render_template("form_update_category.html", categoria=categoria)


@app.route("/select_category_delete")  # PRE DELETE CATEGORIA
def select_category_delete():
    collection = db["categorias"]
    categorias = collection.find()
    return render_template("select_category_delete.html", categorias=categorias)


@app.route("/delete_category/<int:id>")  # BORRAR CATEGORIA
def delete_category(id):
    categorias = db["categorias"]
    productos = db["productos"]

    categoria = categorias.find_one({"id": id})

    criteria = {"category": categoria["category_name"]}
    productos.delete_many(criteria)

    categorias.delete_one({"id": id})
    flash("Categoría y Productos relacionados con la misma borrados con éxito!")
    return redirect(url_for("select_category_delete"))


@app.route("/add_provider", methods=["GET", "POST"])  # ADD PROVEEDOR
def add_provider():

    categorias = db["proveedores"]

    random_id = random.randint(0, 100000000)

    while categorias.find_one({"id": random_id}) is not None:
        random_id = random.randint(0, 100000000)

    if request.method == "POST":
        title = request.form.get("title")
        inserts = {"id": random_id, "provider_name": title}
        categorias.insert_one(inserts)
        flash("Proveedor añadido con éxito!")
        return redirect(url_for("add_provider"))
    return render_template("form_new_provider.html")


@app.route("/select_provider_update")  # PRE UPDATE PROVEEDOR
def select_provider_update():
    collection = db["proveedores"]
    proveedores = collection.find()
    return render_template("select_provider_update.html", proveedores=proveedores)


# UPDATE PROVEEDOR
@app.route("/update_provider/<int:id>", methods=["GET", "POST"])
def update_provider(id):

    proveedores = db["proveedores"]
    productos = db["productos"]

    proveedor = proveedores.find_one({"id": id})

    if request.method == "POST":
        title = request.form.get("title")
        filter = {"id": id}
        update = {"$set": {"id": id, "provider_name": title}}
        proveedores.update_one(filter, update)
        flash("Proveedor actualizado con éxito!")
        filter = {"provider": proveedor["provider_name"]}
        update = {"$set": {"provider": title}}
        productos.update_many(filter, update)
        flash("Prodcutos actualizados al nuevo proveedor con éxito!")

    return render_template("form_update_provider.html", proveedor=proveedor)


@app.route("/select_provider_delete")  # PRE DELETE PROVEEDOR
def select_provider_delete():
    collection = db["proveedores"]
    proveedores = collection.find()
    return render_template("select_provider_delete.html", proveedores=proveedores)


@app.route("/delete_provider/<int:id>")  # BORRAR PROVEEDOR
def delete_provider(id):
    proveedores = db["proveedores"]
    productos = db["productos"]

    proveedor = proveedores.find_one({"id": id})

    criteria = {"category": proveedor["provider_name"]}
    productos.delete_many(criteria)

    proveedores.delete_one({"id": id})
    flash("Proveedor y Productos relacionados con la misma borrados con éxito!")
    return redirect(url_for("select_provider_delete"))


@app.route("/search")  # SEARCH BAR
def search():
    collection = db["productos"]
    query = request.args.get("q")
    if query:
        results = collection.find({"title": {"$regex": query, "$options": "i"}})
    else:
        results = []
    return render_template("search_results.html", query=query, results=results)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
