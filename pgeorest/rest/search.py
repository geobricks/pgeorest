from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.metadata.search import MongoSearch
from bson import json_util
from pgeorest.config.settings import settings


search = Blueprint('search', __name__)

# mongo_search = MongoSearch(connection, db, doc)


def get_connection_properties(dbname):
    connection = settings['db'][dbname]['connection']
    db = settings['db'][dbname]['database']
    doc = settings['db'][dbname]['document']['layer']
    return connection, db, doc
    

@search.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'


@search.route('/<dbname>/layer/id/<id>', methods=['GET'])
@search.route('/<dbname>/layer/id/<id>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_id_service(dbname, id):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layer_by_id(id))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/dekad/<dekad>', methods=['GET'])
@search.route('/<dbname>/layer/dekad/<dekad>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_dekad_service(dbname, dekad):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_product(None, dekad, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/product/<product>', methods=['GET'])
@search.route('/<dbname>/layer/product/<product>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_service(dbname, product):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_product(product, None, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/product/<product>/type/<aggregation_type>', methods=['GET'])
@search.route('/<dbname>/layer/product/<product>/type/<aggregation_type>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_and_type_service(dbname, product, aggregation_type):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_product(product, None, aggregation_type))
    return Response(out, content_type='application/json; charset=utf-8')



@search.route('/<dbname>/layer/product/<product>/dekad/<dekad>', methods=['GET'])
@search.route('/<dbname>/layer/product/<product>/dekad/<dekad>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_and_dekad_service(dbname, product, dekad):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_product(product, dekad, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/product/<product>/dekad/<dekad>/type/<aggregation_type>', methods=['GET'])
@search.route('/<dbname>/layer/product/<product>/dekad/<dekad>/type/<aggregation_type>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_product_and_dekad_and_type_service(dbname, product, dekad, aggregation_type):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_product(product, dekad, aggregation_type))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/from/<dekad_from>/to/<dekad_to>/product/<product>', methods=['GET'])
@search.route('/<dbname>/layer/from/<dekad_from>/to/<dekad_to>/product/<product>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_dekad_range(dekad_from, dekad_to, product):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_dekad_range(dekad_from, dekad_to, product))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/from/<dekad_from>/to/<dekad_to>', methods=['GET'])
@search.route('/<dbname>/layer/from/<dekad_from>/to/<dekad_to>/', methods=['GET'])
@cross_origin(origins='*')
def find_layer_by_dekad_range_and_product(dbname, dekad_from, dekad_to):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_layers_by_dekad_range(dekad_from, dekad_to, None))
    return Response(out, content_type='application/json; charset=utf-8')


@search.route('/<dbname>/layer/distinct/<field>', methods=['GET'])
@search.route('/<dbname>/layer/distinct/<field>/', methods=['GET'])
@cross_origin(origins='*')
def find_distinct(dbname, field):
    connection, db, doc = get_connection_properties(dbname)
    mongo_search = MongoSearch(connection, db, doc)
    out = json_util.dumps(mongo_search.find_all(field))
    return Response(out, content_type='application/json; charset=utf-8')



    