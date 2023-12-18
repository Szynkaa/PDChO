import json

from flask import Flask, Response, jsonify, render_template, request

import models

app = Flask("PDChO App")

app.config['JSON_AS_ASCII'] = False


@app.route("/")
@app.route("/home")
@app.route("/app")
def home():
    return render_template("main.html")


@app.route("/api/ingredients", methods=["GET"])
def get_ingredients():
    return jsonify(models.Ingredient.get_all())


@app.route("/api/ingredients/<string:name>", methods=["GET"])
def get_dishes_for_ingredient(name):
    return jsonify(models.Ingredient(name).get_dishes())


@app.route("/api/dishes/<string:name>", methods=["GET"])
def get_dish_contains(name):
    dish = models.Dish(name)
    return jsonify(dish.get_contains())


@app.route("/api/dishes", methods=["POST"])
def add_dish():
    data: dict = json.loads(request.data)
    connection = models.Connection(data.get("name"), data.get("type", None))
    for ingredient in data.get("ingredients", []):
        connection.add_ingredient(ingredient)
    for subdish in data.get("subdishes", []):
        connection.add_subdish(subdish)
    print(connection.dish_name, connection.dish_type)

    connection.save()

    return Response(status=200)


@app.route("/api/dishes/<string:name>", methods=["DELETE"])
def delete_dish(name):
    dish = models.Dish(name)
    dish.delete()
    return Response(status=200)
