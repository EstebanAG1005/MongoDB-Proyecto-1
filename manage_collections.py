from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import random
import logging
import urllib.parse
import pymongo
import json

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

collection1 = db["categorias"]
collection2 = db["productos"]
collection3 = db["proveedores"]

# open and read the JSON file
with open("data\categorias.json") as file:
    data = json.load(file)


# open and read the JSON file
with open("data\productos.json") as file:
    data1 = json.load(file)


# open and read the JSON file
with open("data\proveedores.json") as file:
    data2 = json.load(file)

# use the bulk_write method to perform a bulk insert
bulk_insert = collection1.bulk_write([pymongo.InsertOne(record) for record in data])
bulk_insert = collection2.bulk_write([pymongo.InsertOne(record) for record in data1])
bulk_insert = collection3.bulk_write([pymongo.InsertOne(record) for record in data2])
