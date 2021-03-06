import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeorest.config.settings import settings
from pgeo.db.postgresql.common import DBConnection
from flask import request
import inspect

app = Blueprint(__name__, __name__)
log = log.logger(__name__)

@app.route('/')
def index():
    return 'Welcome to the Spatial Query module!'


@app.route('/db/<datasource>/<query>/', methods=['GET'])
@app.route('/db/<datasource>/<query>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def query_db(datasource, query):
    """
    Query the PostGIS with a custom query
    :param datasource: postgis/postgres datasource
    :param query: query to be passed to the db
    :return:
    """
    # TODO it's not used the schema in the query.
    # it should be replaced if the query contains {{SCHEMA}} or something like that
    try:
        spatial_db = DBConnection(settings["db"][datasource])
        result = spatial_db.query(query)
        return Response(json.dumps(result), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())

