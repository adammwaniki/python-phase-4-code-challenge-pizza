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
        # including a condition for the 'only" parameter whereby the id name and address are the only ones to be returned because there are other things in the list
        response_dict_list = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in Restaurant.query.all()]

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

        # Making sure the restaurant exixts before deleting it
        if restaurant_specific:
            db.session.delete(restaurant_specific)
            db.session.commit()
            response = make_response({}, 204)
        else:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        return response
    
api.add_resource(RestaurantsByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        # Remembering to add the only condition like on line 33,34
        response_dict_list = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in Pizza.query.all()]

        response = make_response(
            jsonify(response_dict_list),
            200
        )

        return response
    
api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        # Switching to request.get_json() because the app makes use of json data as well as form data
        # The price must be an integer as indicated in the models so we will do type conversion here
        restaurant_pizza_data = request.get_json()
        try:
            price = restaurant_pizza_data.get('price')
            pizza_id = restaurant_pizza_data.get('pizza_id')
            restaurant_id = restaurant_pizza_data.get('restaurant_id')
            # added validation
            if price < 1 or price > 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
        

            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        
            db.session.add(restaurant_pizza)
            db.session.commit()

            response_dict = restaurant_pizza.to_dict()
            return make_response(
            jsonify(response_dict),
            201
            )

        except KeyError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [f"Missing key: {str(e)}"]}), 404)
        finally:
            db.session.close()
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)










# Notes on alternative solutions that  work but don't pass all the tests 
'''
class RestaurantPizzas(Resource):
    def post(self):
        # Switching to request.get_json() because the app makes use of json data as well as form data
        # The price must be an integer as indicated in the models so we will do type conversion here
        restaurant_pizza_data = request.get_json()

        price = restaurant_pizza_data.get('price')
        pizza_id = restaurant_pizza_data.get('pizza_id')
        restaurant_id = restaurant_pizza_data.get('restaurant_id')

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_dict = restaurant_pizza.to_dict()
        response = make_response(
            jsonify(response_dict),
            201
        )
        
        return response if response else make_response(
            jsonify({"errors": ["validation errors"]}),
            400
        )
        
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')
        
'''

'''
def post(self):
        # I thought we were working with form data so I wasn't using request.get_json() here
        # The price must be an integer as indicated in the models so we will do type conversion here
        new_restaurant_pizza_data = RestaurantPizza(
            price = int(request.form['price']),
            pizza_id = request.form['pizza_id'],
            restaurant_id = request.form['restaurant_id'],
        )
        db.session.add(new_restaurant_pizza_data)
        db.session.commit()

        response_dict = new_restaurant_pizza_data.to_dict()
        response = make_response(
            jsonify(response_dict),
            201
        )
        
        return response if response else make_response(
            jsonify({"errors": ["validation errors"]}),
            400
        )
'''