import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
import copy
import StringIO
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeorest.config.settings import settings
from pgeo.stats.raster import Stats
from pgeo.gis.raster import crop_by_vector_database, get_histogram
from pgeo.gis import gdal_calc
from pgeo.utils.filesystem import create_tmp_filename
from flask import request

app = Blueprint(__name__, __name__)
log = log.logger(__name__)


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
    return 'Welcome to the GHG module!'


@app.route('/rasters/burned_areas/<layer_fire>/land_cover/<layer_land_cover>/gaul/<gaul>/codes/<codes>/', methods=['GET'])
@app.route('/rasters/burned_areas/<layer_fire>/land_cover/<layer_land_cover>/gaul/<gaul>/codes/<codes>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_ghg_stats_all(layer_fire, layer_land_cover, gaul, codes):
    try:
        # Module to process statistics
        stats = Stats(settings)
        db_spatial = stats.db_spatial

        log.info(gaul)
        log.info(codes)

        codes = codes.split(",")

        s = []
        for code in codes:
            # TODO: should be transformed to the right SRID (now they have the same prj)
            # spatial_query: '{ "query_extent" : "SELECT ST_AsGeoJSON(ST_Transform(ST_SetSRID(ST_Extent(geom), 3857), {{SRID}})) FROM {{SCHEMA}}.gaul0_3857_test WHERE adm0_code IN ({{CODES}})", "query_layer" : "SELECT * FROM {{SCHEMA}}.gaul0_3857_test WHERE adm0_code IN ({{CODES}})"}'
            query_extent = "SELECT ST_AsGeoJSON(ST_Extent(geom)) FROM spatial.gaul" + gaul + "_3857 WHERE adm1_code IN (" + code + ")"
            query_layer = "SELECT * FROM spatial.gaul" + gaul + "_3857 WHERE adm1_code IN (" + code + ")"

            # crop layer fire to gaul
            layer_fire_path = stats.get_raster_path(layer_fire)
            log.info(layer_fire_path)
            layer_fire_cropped = crop_by_vector_database(layer_fire_path, db_spatial, query_extent, query_layer)
            log.info(layer_fire_cropped)

            # crop layer land cover to gaul
            layer_land_cover_path = stats.get_raster_path(layer_land_cover)
            log.info(layer_land_cover_path)
            layer_land_cover_cropped = crop_by_vector_database(layer_land_cover_path, db_spatial, query_extent, query_layer)
            log.info(layer_land_cover_cropped)

            # compute layer operation
            output_file = create_tmp_filename();
            log.info(output_file)
            gdal_calc.calc_layers([layer_fire_cropped, layer_land_cover_cropped], output_file, "mult")


            # get stats
            json_stats = raster_histogram
            json_stats["raster"]["path"] = output_file
            json_stats["stats"]["buckets"] = int(16)
            json_stats["stats"]["min"] = float(1.0)
            json_stats["stats"]["max"] = float(16.0)
            land_cover_ba = get_histogram(output_file, json_stats["stats"])
            s.append(land_cover_ba)
            # s.append({"land_cover_ba": land_cover_ba})
            #
            # json_stats = raster_histogram
            # json_stats["raster"]["path"] = layer_fire_cropped
            # json_stats["stats"]["buckets"] = int(2)
            # json_stats["stats"]["min"] = float(0.0)
            # json_stats["stats"]["max"] = float(2.0)
            # s.append({ "ba" : stats.get_histogram(json_stats)})
            #
            # json_stats = raster_histogram
            # json_stats["raster"]["path"] = layer_land_cover_path
            # json_stats["stats"]["buckets"] = int(16)
            # json_stats["stats"]["min"] = float(1.0)
            # json_stats["stats"]["max"] = float(16.0)
            # s.append({ "land_cover" : stats.get_histogram(json_stats)})

        return Response(json.dumps(s), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())