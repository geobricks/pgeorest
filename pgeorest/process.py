import json
from flask import Blueprint
from flask.ext.cors import cross_origin
from flask import request
from flask import Response
from pgeo.error.custom_exceptions import PGeoException
from pgeo.config.settings import read_config_file_json
from pgeo.gis.processing import process
from pgeo.utils import log


processing = Blueprint('processing', __name__)
log = log.logger('process.py')


@processing.route('/')
def index():
    return 'Welcome to the Process module!'


@processing.route('/list/<source_name>', methods=['GET'])
@processing.route('/list/<source_name>/', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def list_steps_service(source_name):
    try:
        conf = read_config_file_json(source_name, 'data_providers')
        obj = conf['processing']
        try:
            return Response(json.dumps(obj), content_type='application/json; charset=utf-8')
        except Exception, e:
            raise PGeoException(e.message, 500)
    except Exception, e:
        raise PGeoException(e.message, 500)


@processing.route('/<source_name>', methods=['POST'])
@processing.route('/<source_name>/', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def process_service(source_name):
    try:
        payload = request.get_json()
        out = process(payload)
        try:
            return Response(json.dumps(out), content_type='application/json; charset=utf-8')
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)
    except Exception, e:
        log.error(e)
        raise PGeoException(e.message, 500)