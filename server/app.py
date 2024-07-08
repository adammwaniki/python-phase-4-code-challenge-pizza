#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# I will make this app restful so as to follow the principle of API first, frontend second
# which is best practice for larger applications
# i have added the jsonify import as well
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        # making use of a list of restaurant dictionaries since that's what the code challenge wants 
        # to be parsed as json
        response_dict_list = [restaurant.to_dict() for restaurant in Restaurant.query.all()]

        # Creating a jsonified response
        response = make_response(
            jsonify(response_dict_list), 
            200
        )

        return response
# Remembering to add the api resource
api.add_resource(Restaurants, '/restaurants')

class RestaurantsByID(Resource):
    def get(self, id):
        # making use of a dictionary since they will be inside the list of dictionaries from the Restaurants class
        restaurant_specific = Restaurant.query.filter_by(id=id).first()
        
        if restaurant_specific:
            # we handle the conversion to dict here instead of in the previous attribute because of the possibility
            # of a single restaurant that doesn't exist being returned which would result in a 500 error instead of 404
            # because of the None
            response_dict = restaurant_specific.to_dict()

            response = make_response(
                jsonify(response_dict),
                200
            )
        else:
            response = make_response(
                jsonify({"error": "Restaurant not found"}),
                404
            )

        return response
    
    def delete(self, id):
        restaurant_specific = Restaurant.query.filter(Restaurant.id == id).first()

        db.session.delete(restaurant_specific)
        db.session.commit()

        response_dict = {"error": "Restaurant not found"}

        response = make_response(
            response_dict,
            204
        )

        return response
    
api.add_resource(RestaurantsByID, '/restaurants/<int:id>')

class Pizzas:
    def get(self):
        pass


if __name__ == "__main__":
    app.run(port=5555, debug=True)
