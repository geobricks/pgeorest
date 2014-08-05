import json
from flask import Blueprint
from flask import Response
from flask import request
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors


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
        req_json = json.loads(request.get_json())
        return Response(json.dumps(req_json['name']), content_type='application/json; charset=utf-8')
    except:
        raise PGeoException(errors[513], status_code=513)