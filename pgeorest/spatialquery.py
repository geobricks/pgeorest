import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeo.config.settings import settings
from pgeo.db.postgresql.common import DBConnection
from flask import request

app = Blueprint(__name__, __name__)
log = log.logger(__name__)
# spatial_db = DBConnection(settings["db"]["spatial"])
#
# print "here"
# print spatial_db

@app.route('/')
def index():
    return 'Welcome to the Spatial Query module!'


@app.route('/db/<datasource>/<query>/', methods=['GET'])
@app.route('/db/<datasource>/<query>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def query_db(datasource, query):
    try:

        spatial_db = DBConnection(settings["db"][datasource])

        print
        # result = spatial_db.query("select adm0_code from spatial.gaul2_3857_test")
        result = spatial_db.query(query)
        return Response(json.dumps(result), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


