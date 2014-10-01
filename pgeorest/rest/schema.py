import json
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeorest.config.settings import settings
from importlib import import_module
# from pgeomodis.config.modis_config import config as config_data


schema = Blueprint('schema', __name__)


@schema.route('/')
@cross_origin(origins='*')
def index():
    return 'Welcome to the Schema module!'


@schema.route('/sources/', methods=['GET'])
@cross_origin(origins='*')
def list_sources_service():
    try:
        out = []
        for module in settings['modules']:
            out.append({
                'code': module['label'] + '.json',
                'label': module['label']
            })
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@schema.route('/sources/<source_name>/', methods=['GET'])
@cross_origin(origins='*')
def list_services(source_name):
    try:
        # source_name = source_name[0:source_name.index('.json')] if '.json' in source_name else source_name
        # source_name = source_name.lower()
        # mod = import_module('pgeo' + source_name + '.config')
        # config_folder = mod.__file__[0:mod.__file__.rindex('/')]
        # config_data = json.loads(open(config_folder + '/' + source_name + '.json').read())
        out = {
            # 'bands': config_data['bands'],
            # 'base_url': config_data['services_base_url'],
            # 'ftp': config_data['source']['ftp'],
            # 'services': config_data['services'],
            # 'subfolders': config_data['subfolders']
        }
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except Exception, err:
        print err
        raise PGeoException(errors[511], status_code=511)