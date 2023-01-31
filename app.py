from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["inventario_empresa"]


# INDEX
@app.route("/")
def index():
    collection = db["productos"]
    productos = collection.find()
    return render_template("index.html", productos=productos)

# SEARCH BAR


@app.route('/search')
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
