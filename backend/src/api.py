import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_all_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = [drink.long() for drink in Drink.query.all()]

    # if (len(drinks) == 0):
    #     abort(404)

    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    body = request.get_json()

    if body is None or 'title' not in body or 'recipe' not in body:
        abort(400)

    try:
        recipe = json.dumps(body['recipe'])
        drink = Drink(title=body['title'], recipe=recipe)
        drink.insert()

        return jsonify({"success": True, "drinks": [drink.long() for drink in Drink.query.all()]})
    except:
        # print(sys.exc_info())
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(drink_id):
    drink = Drink.query.filter_by(id=drink_id).first_or_404()
    body = request.get_json()

    if (body is None):
        abort(400)

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    drink.update()

    return jsonify({"success": True, "drinks": [drink.long() for drink in Drink.query.all()]})


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(drink_id):
    drink = Drink.query.filter_by(id=drink_id).first_or_404()
    drink.delete()
    return jsonify({"success": True, "delete": drink_id})


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }),
        400,
    )


@app.errorhandler(AuthError)
def unauthorized(error):
    return (
        jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }),
        error.status_code,
    )


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(422)
def unprocessable_entity(error):
    return (
        jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable entity"
        }),
        422,
    )


@app.errorhandler(500)
def server_error(error):
    return (
        jsonify({
            "success": False,
            "error": 500,
            "message": "Server error"
        }),
        500,
    )
