import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
import copy
import StringIO
import uuid
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeorest.config.settings import settings
from pgeo.stats.raster import Stats
from pgeo.gis.raster_scatter import create_scatter
from pgeo.gis.raster_mapalgebra import filter_layers
from flask import request
from pgeo.manager.manager import Manager

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
    """
    TODO is it useful of should be used the one below? @Deprecated?
    Get raster statistic filtered by a spatial query:
    TODO add json definition of the spatial query and statistics that can be applied
    :return: a json with the zonal statistics
    """
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
    """
    Get raster statistic filtered by a spatial query:
    TODO add json definition of the spatial query and statistics that can be applied
    :return: a json with the zonal statistics
    """
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
        """
        Create a scatter plot from two rasters of the same dimension
        @param layers: workspace:layername1,workspace:layername2
        @return: json with the scatter plot data
        """

        if ":" not in layers:
            return PGeoException("Please Specify a workspace for " + str(layers), status_code=500)
        input_layers = layers.split(",")

        stats = Stats(settings)
        raster_path1 = stats.get_raster_path(input_layers[0])
        raster_path2 = stats.get_raster_path(input_layers[1])

        # creating scatter
        response = create_scatter(raster_path1, raster_path2, 300)

        return Response(json.dumps(response), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/rasters/mapalgebra/layers/<layers>/minmax/<minmax>', methods=['GET'])
@app.route('/rasters/mapalgebra/layers/<layers>/minmax/<minmax>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_filter_layers(layers, minmax):
    try:
        """
        Create a temporary mask layer using min-max of the layers
        @param layers: workspace:layername1,workspace:layername2
        @param minmax: min1,max1,min2,max2
        @return: json with the scatter plot data
        """

        if ":" not in layers:
            return PGeoException("Please Specify a workspace for " + str(layers), status_code=500)
        input_layers = layers.split(",")
        minmax_values = minmax.split(",")

        stats = Stats(settings)

        # getting raster information
        raster_path1 = stats.get_raster_path(input_layers[0])
        raster_path2 = stats.get_raster_path(input_layers[1])

        # getting raster min max values
        min1 = float(minmax_values[0])
        max1 = float(minmax_values[1])
        min2 = float(minmax_values[2])
        max2 = float(minmax_values[3])

        # create the layer
        path = filter_layers(raster_path1, raster_path2, min1, max1, min2, max2)

        # creating metdata
        uid = str(uuid.uuid4())
        metadata_def = {}
        metadata_def["uid"] = "tmp:" + uid
        metadata_def["title"] = {}
        metadata_def["title"]["EN"] = "masked_" + uid
        metadata_def["meSpatialRepresentation"] = {}

        # publish the new tmp layer
        # TODO: metadata? style to be applied?
        # TODO: how to handle a tmp workspace overhead?
        s = copy.deepcopy(settings)
        # this copies the geoserver_tmp dato to "geoserver" settings to be passed to the manager
        s["geoserver"] = s["geoserver_tmp"]
        manager = Manager(s)
        manager.publish_coverage(path, metadata_def, False, True, False)

        return Response(json.dumps(metadata_def), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


