import json
from flask import Blueprint
from flask.ext.cors import cross_origin
from flask import request
from flask import Response
import calendar
import datetime
from pgeo.error.custom_exceptions import PGeoException
from pgeorest.config.settings import read_config_file_json
from pgeo.gis.processing import process
from pgeo.manager.manager import Manager
from pgeorest.config.settings import settings
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


@processing.route('/publish/<title>/<style>/<path>', methods=['GET', 'POST'])
@processing.route('/publish/<title>/<style>/<path>/', methods=['GET', 'POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def publish_service(title, style, path):
    try:
        path = path.replace(':', '/')
        try:
            manager = Manager(settings)
            metadata_def = get_metadata(manager.metadata, title, style)
            manager.publish_coverage(path, metadata_def)

            return Response(json.dumps(path), content_type='application/json; charset=utf-8')
        except Exception, e:
            log.error(e)
            raise PGeoException(e.message, 500)
    except Exception, e:
        log.error(e)
        raise PGeoException(e.message, 500)


def get_metadata(metadata, title, style):

    creationDate = calendar.timegm(datetime.datetime.now().timetuple())

    metadata_def = {}
    metadata_def["title"] = {}
    metadata_def["title"]["EN"] = title
    metadata_def["creationDate"] = creationDate
    metadata_def["meContent"] = {}
    metadata_def["meContent"]["seCoverage"] = {}
    metadata_def["meContent"]["seCoverage"]["coverageTime"] = {}
    metadata_def["meContent"]["seCoverage"]["coverageTime"]["from"] = creationDate
    metadata_def["meContent"]["seCoverage"]["coverageTime"]["to"] = creationDate

    metadata_def["meContent"]["seCoverage"]["coverageSector"] = {}
    metadata_def["meContent"]["seCoverage"]["coverageSector"]["codeList"] = "Products"
    metadata_def["meContent"]["seCoverage"]["coverageSector"]["codes"] = [{"code" : "MODIS"}]
    metadata_def["meContent"]["seCoverage"]["coverageSector"]["codes"] = [{"code" : "MODIS"}]


    # TODO: in theory should be the original file the onlineResource
    metadata_def["meAccessibility"] = {}
    metadata_def["meAccessibility"]["seDistribution"] = {}
    # metadata_def["meAccessibility"]["seDistribution"]["onlineResource"] = "/media/vortex/16DE-3364/MODIS_250m.tif"

    # TODO: added new field for the original resource (should we have two different metadata?)
    #metadata_def["meAccessibility"]["seDistribution"]["originalResource"] = output_filename

    # adding type of layer
    aggregationProcessing = "none"
    metadata_def["meStatisticalProcessing"] = {}
    metadata_def["meStatisticalProcessing"]["seDatasource"] = {}
    metadata_def["meStatisticalProcessing"]["seDatasource"]["seDataCompilation"] = {}
    metadata_def["meStatisticalProcessing"]["seDatasource"]["seDataCompilation"]["aggregationProcessing"] = aggregationProcessing;

    # default style
    metadata_def["meSpatialRepresentation"] = {}
    metadata_def["meSpatialRepresentation"]["seDefaultStyle"] = {}
    if aggregationProcessing == "da":
        metadata_def["meSpatialRepresentation"]["seDefaultStyle"]["name"] = style + "_" + aggregationProcessing
    else:
        metadata_def["meSpatialRepresentation"]["seDefaultStyle"]["name"] = style


    # merging metadata to the base raster one
    metadata_def = metadata.merge_layer_metadata("raster", metadata_def)
    return metadata_def