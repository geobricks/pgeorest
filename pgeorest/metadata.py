import json
from flask import Blueprint
from flask import Response
from flask import request
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.db.mongo.metadata.db import insert_metadata
from pgeo.metadata.metadata import merge_layer_metadata


metadata = Blueprint('metadata', __name__)


@metadata.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Metadata module!'


@metadata.route('/create', methods=['POST'])
@metadata.route('/create/', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def create():
    try:
        user_json = request.get_json()
        test = merge_layer_metadata('modis', user_json)
        insert_metadata(user_json)
        return Response(json.dumps(test), content_type='application/json; charset=utf-8')
    except:
        raise PGeoException(errors[513], status_code=513)