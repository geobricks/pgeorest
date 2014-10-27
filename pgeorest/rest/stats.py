import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
import copy
import StringIO
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeorest.config.settings import settings
from pgeo.stats.raster import Stats
from pgeo.gis.raster_scatter import create_scatter
from flask import request

app = Blueprint(__name__, __name__)
log = log.logger(__name__)

#TODO: Review the REST for also layers that are not published, but are on the filesystem


# default json_statistics
raster_statistics = {
    "raster": {
        "uid": None
    },
    "stats": {
        "force": True
    }
}


raster_histogram = {
    "raster": {
        "uid": None
    },
    "stats": {
        "force": True,
        "buckets": 256
    }
}

@app.route('/')
def index():
    """
        Welcome message
        @return: welcome message
    """
    return 'Welcome to the stats module!'


# @app.route('/raster/<layer>', methods=['GET'], headers=['Content-Type'])
# @app.route('/raster/<layer>/',  methods=['GET'], headers=['Content-Type'])
# @cross_origin(origins='*', headers=['Content-Type'])
@app.route('/raster/<layer>/',  methods=['GET'])
@app.route('/raster/<layer>', methods=['GET'])
def get_stats(layer):
    """
    Extracts all the statistics of a layer
    @param layer: workspace:layername
    @return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = copy.deepcopy(raster_statistics)
        json_stats["raster"]["uid"] = layer

        # Module to process statistics
        stats = Stats(settings)
        return Response(json.dumps(stats.get_stats(json_stats)), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())

@app.route('/raster/<layer>/hist/', methods=['GET'])
@app.route('/raster/<layer>/hist', methods=['GET'])
@cross_origin()
def get_histogram(layer):
    """
    Extracts histogram from a layer
    @param layer: workspace:layername
    @return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = copy.deepcopy(raster_histogram)
        json_stats["raster"]["uid"] = layer
        # Module to process statistics
        stats = Stats(settings)
        return Response(json.dumps(stats.get_histogram(json_stats)), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())

@app.route('/raster/<layer>/hist/<buckets>/', methods=['GET'])
@app.route('/raster/<layer>/hist/<buckets>', methods=['GET'])
@cross_origin(origins='*')
def get_histogram_buckets(layer, buckets):
    """
    Extracts histogram from a layer
    TODO: add a boolean and buckets
    default: boolean = True, buckets = 256
    @param layer: workspace:layername
    @param buckets: number of buckets i.e. 256
    @return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = copy.deepcopy(raster_histogram)
        json_stats["raster"]["uid"] = layer
        json_stats["stats"]["buckets"] = int(buckets)

        # Module to process statistics
        stats = Stats(settings)
        return Response(json.dumps(stats.get_histogram(json_stats)), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/raster/<layer>/hist/buckets/<buckets>/min/<min>/max/<max>/', methods=['GET'])
@app.route('/raster/<layer>/hist/buckets/<buckets>/min/<min>/max/<max>', methods=['GET'])
@cross_origin(origins='*')
def get_histogram_buckets_min_max(layer, buckets, min, max):
    """
    Extracts histogram from a layer
    TODO: add a boolean and buckets
    default: boolean = True, buckets = 256
    @param layer: workspace:layername
    @param buckets: number of buckets i.e. 256
    @return: json with the raster statistics
    """
    try:
        if ":" not in layer:
            return PGeoException("Please Specify a workspace for " + str(layer), status_code=500)

        json_stats = copy.deepcopy(raster_histogram)
        json_stats["raster"]["uid"] = layer
        json_stats["stats"]["buckets"] = int(buckets)
        json_stats["stats"]["min"] = float(min)
        json_stats["stats"]["max"] = float(max)

        # Module to process statistics
        stats = Stats(settings)
        return Response(json.dumps(stats.get_histogram(json_stats)), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())

@app.route('/rasters/<layers>/lat/<lat>/lon/<lon>/', methods=['GET'])
@app.route('/rasters/<layers>/lat/<lat>/lon/<lon>', methods=['GET'])
@cross_origin(origins='*')
def get_lat_lon(layers, lat, lon):
    """
    Get the value of the layer at lat/lon position
    @param layer: workspace:layername
    @param lat: latitude
    @param lon: longitude
    @return: json with the raster statistics
    """
    try:
        if ":" not in layers:
            return PGeoException("Please Specify a workspace for " + str(layers), status_code=500)

        input_layers = layers.split(",")

        # Module to process statistics
        stats = Stats(settings)
        s = stats.get_location_values(input_layers, lat, lon)
        return Response(json.dumps(s), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/raster/spatial_query/', methods=['POST'])
@app.route('/raster/spatial_query', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_stats_by_layer():
    try:
        user_json = request.get_json()

        # Module to process statistics
        stats = Stats(settings)
        s = stats.zonal_stats(user_json)
        return Response(json.dumps(s), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/rasters/spatial_query/', methods=['POST'])
@app.route('/rasters/spatial_query', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_stats_by_layers():
    try:
        # Module to process statistics
        stats = Stats(settings)

        user_json = request.get_json()
        response = []
        for uid in user_json["raster"]["uids"]:
            json_stat = copy.deepcopy(user_json)
            json_stat["raster"]["uid"] = uid
            s = {}
            s[uid] = stats.zonal_stats(json_stat)
            response.append(s)
        return Response(json.dumps(response), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/rasters/scatter_analysis/', methods=['POST'])
@app.route('/rasters/scatter_analysis', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_scatter_analysis():
    try:
        # Module to process statistics
        stats = Stats(settings)

        user_json = request.get_json()
        log.info(user_json)
        response = []
        for uid in user_json["raster"]["uids"]:
            log.info(user_json)
            json_stat = copy.deepcopy(user_json)
            json_stat["raster"]["uid"] = uid
            response.append(stats.zonal_stats(json_stat))

        log.info(response[0])
        log.info(response[1])
        # io.BytesIO()
        si = StringIO.StringIO()
        result = stats.create_csv_merge(si, response[0], response[1])
        log.info(result.getvalue())

        return Response(result.getvalue())
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



@app.route('/rasters/scatter_plot/<layers>/', methods=['GET'])
@app.route('/rasters/scatter_plot/<layers>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_scatter_plot(layers):
    try:

        if ":" not in layers:
            return PGeoException("Please Specify a workspace for " + str(layers), status_code=500)
        input_layers = layers.split(",")

        stats = Stats(settings)
        raster_path1 = stats.get_raster_path(input_layers[0])
        raster_path2 = stats.get_raster_path(input_layers[1])

        response = create_scatter(raster_path1, raster_path2, 1, 1, 300)
        #response = create_scatter(raster_path1, raster_path2, 1, 1, 20)

        Response(json.dumps(response), content_type='application/json; charset=utf-8')

        return Response(json.dumps(response), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



@app.route('/rasters/scatter_plot/<layers>/workers/<workers>', methods=['GET'])
@app.route('/rasters/scatter_plot/<layers>/workers/<workers>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_scatter_plot_workers(layers, workers):
    try:

        if ":" not in layers:
            return PGeoException("Please Specify a workspace for " + str(layers), status_code=500)
        input_layers = layers.split(",")

        stats = Stats(settings)
        raster_path1 = stats.get_raster_path(input_layers[0])
        raster_path2 = stats.get_raster_path(input_layers[1])

        response = create_scatter(raster_path1, raster_path2, 1, 1, 300, 6, int(workers))
        #response = create_scatter(raster_path1, raster_path2, 1, 1, 20)

        Response(json.dumps(response), content_type='application/json; charset=utf-8')

        return Response(json.dumps(response), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


