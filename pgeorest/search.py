from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.db.mongo.search import find_layer_by_id
from pgeo.db.mongo.search import find_layers_by_product
from bson import json_util


search = Blueprint('search', __name__)


@search.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'


@search.route('/layer/id/<id>', methods=['GET'])
@search.route('/layer/id/<id>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_id_service(id):
    out = json_util.dumps(find_layer_by_id(id))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/layer/dekad/<dekad>', methods=['GET'])
@search.route('/layer/dekad/<dekad>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_dekad_service(dekad):
    out = json_util.dumps(find_layers_by_product(None, dekad, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/layer/product/<product>', methods=['GET'])
@search.route('/layer/product/<product>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_service(product):
    out = json_util.dumps(find_layers_by_product(product, None, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/layer/product/<product>/dekad/<dekad>', methods=['GET'])
@search.route('/layer/product/<product>/dekad/<dekad>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_and_dekad_service(product, dekad):
    out = json_util.dumps(find_layers_by_product(product, dekad, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/layer/product/<product>/dekad/<dekad>/type/<aggregation_type>', methods=['GET'])
@search.route('/layer/product/<product>/dekad/<dekad>/type/<aggregation_type>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_and_dekad_and_type_service(product, dekad, aggregation_type):
    out = json_util.dumps(find_layers_by_product(product, dekad, aggregation_type))
    return Response(out, content_type='application/json; charset=utf-8')