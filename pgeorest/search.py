from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.db.mongo.search import find_layer_by_id
from pgeo.db.mongo.search import find_layers_by_dekad
from bson import json_util


search = Blueprint('search', __name__)


@search.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'


@search.route('/layer/byid/<id>', methods=['GET'])
@search.route('/layer/byid/<id>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_id_service(id):
    out = json_util.dumps(find_layer_by_id(id))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/layer/bydekad/<dekad>', methods=['GET'])
@search.route('/layer/bydekad/<dekad>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_dekad_service(dekad):
    out = json_util.dumps(find_layers_by_dekad(dekad))
    return Response(out, content_type='application/json; charset=utf-8')