from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["restaurant"]


@app.route("/")
def index():
    collection = db["users"]
    data = collection.find()
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
