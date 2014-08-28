import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
import copy
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeo.config.settings import settings
from flask import request, send_from_directory
from shutil import move
import os
import uuid
from pgeo.gis.raster import crop_by_vector_database
from pgeo.stats.raster import Stats
from pgeo.utils.filesystem import create_folder_in_tmp, get_filename, zip_files
from pgeo.utils import email_utils

app = Blueprint(__name__, __name__)
log = log.logger(__name__)


stats = Stats(settings)
db_spatial = stats.db_spatial
distribution_folder = settings["folders"]["distribution"]
zip_filename = "layers.zip"

@app.route('/')
def index():
    """
        Welcome message
        @return: welcome message
    """
    return 'Welcome to the distribution module!'


@app.route('/raster/<uids>/spatial_query/<spatial_query>/', methods=['GET'])
@app.route('/raster/<uids>/spatial_query/<spatial_query>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_layers(uids, spatial_query):
    try:
        log.info(uids)
        log.info(spatial_query)
        uids = uids.split(";")
        log.info(uids)
        log.info(spatial_query)
        json_filter = json.loads(spatial_query)

        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        output_files = []
        for uid in uids:
            log.info(uid)
            raster_path = stats.get_raster_path(uid)
            log.info(db_spatial.schema)
            query_extent = json_filter["vector"]["query_extent"]
            query_layer = json_filter["vector"]["query_layer"]

            query_extent = query_extent.replace("{{SCHEMA}}", db_spatial.schema)
            query_layer = query_layer.replace("{{SCHEMA}}", db_spatial.schema)

            # create the file on tm folder
            filepath = crop_by_vector_database(raster_path, db_spatial, query_extent, query_layer)


            # move file to distribution tmp folder
            path, filename, name = get_filename(filepath, True)
            dst_file = os.path.join(output_folder, filename)
            #dst_file = tmp_folder

            log.info(filepath)
            log.info(dst_file)
            move(filepath, dst_file)

            # rename file based on uid layer_name (i.e. fenix:trmm_08_2014 -> fenix_trmm_08_2014)
            output_filename = uid.replace(":", "_") + ".geotiff"
            output_file = os.path.join(output_folder, output_filename)
            os.rename(dst_file, output_file)

            # saving the output file to zip
            output_files.append(output_file)

        # zip folder or files
        zip_files(zip_filename, output_files, zip_folder )

        # send email
        #html = "<html><head></head><body><p>Hi!<br><a href='http://168.202.28.214:5005/distribution/download/" + zip_folder_id + "'>Download!!</a></p></body></html>"
        # html = "<a href='http://168.202.28.214:5005/distribution/download/" + zip_folder_id +"'></a>"
        #email_utils.send_email("simone.murzilli@gmail.com", "guido.barbaglia@gmail.com", "<password>", "Download your layers", html)

        url = request.host_url +"distribution/download/" + zip_folder_id
        return Response(json.dumps('{ "url" : "'+ url + '"}'), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



@app.route('/download/<id>', methods=['GET'])
@app.route('/download/<id>/', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_zip_file(id):
    try:
        log.info(request.base_url)
        log.info(request.path)
        # log.info(distribution_folder + str(id) +"/" + zip_filename)
        return send_from_directory(directory=distribution_folder + str(id), filename=zip_filename)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())
