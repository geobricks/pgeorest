import json
from flask import Blueprint, Response
from flask.ext.cors import cross_origin
import copy
from pgeo.error.custom_exceptions import PGeoException, errors
from pgeo.utils import log
from pgeorest.config.settings import settings
from flask import request, send_from_directory
from shutil import move
import os
import uuid
from pgeo.gis.raster import crop_by_vector_database, get_authority
from pgeo.stats.raster import Stats
from pgeo.utils.filesystem import create_folder_in_tmp, get_filename, zip_files, make_archive
from pgeo.utils import email_utils
from pgeo.gis.vector import create_shapefiles_from_postgis_tables

app = Blueprint(__name__, __name__)
log = log.logger(__name__)


# stats = Stats(settings)
#db_spatial = stats.db_spatial
distribution_folder = settings["folders"]["distribution"]
zip_filename = "layers"

email_user = settings["email"]["user"]
email_password = settings["email"]["password"]

email_header = "Raster layers"
email_body = "<html><head></head>" \
             "<body>" \
             "<div><b>PGeo - Distribution Service</b></div>" \
             "<div style='padding-top:10px;'>The layers you asked to download are available at the following link:</div>" \
             "<div style='padding-top:10px;'><a href='{{LINK}}'>Download Zip File</a></div>" \
             "<div style='padding-top:10px;'><b>Please note that the link will work for the next 24h hours</b></div>" \
             "</body>" \
             "</html>"

@app.route('/')
def index():
    """
        Welcome message
        @return: welcome message
    """
    return 'Welcome to the distribution module!'


@app.route('/rasters/spatial_query/', methods=['POST'])
@app.route('/rasters/spatial_query', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_layers_post():
    try:
        stats = Stats(settings)
        db_spatial = stats.db_spatial
        # TODO: it should be a Thread

        user_json = request.get_json()
        uids = user_json["raster"]["uids"]
        json_filter = json.loads(user_json["vector"])
        email_address = None if "email_address" not in user_json else user_json["email_address"]

        log.info(uids)
        log.info(json_filter)
        log.info(email_address)

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

            authority_name, authority_code  = get_authority(raster_path)
            log.info(db_spatial.schema)
            log.info(authority_name)
            log.info(authority_code)

            query_extent = json_filter["query_extent"]
            query_layer = json_filter["query_layer"]

            query_extent = query_extent.replace("{{SCHEMA}}", db_spatial.schema)
            query_extent = query_extent.replace("{{SRID}}", authority_code)
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

            # rename file based on uid layer_name (i.e. fenix:trmm_08_2014 -> trmm_08_2014)
            output_filename = uid.split(":")[1] + ".tif"
            output_file = os.path.join(output_folder, output_filename)
            os.rename(dst_file, output_file)

            # saving the output file to zip
            output_files.append(output_file)

        # zip folder or files
        # TODO: change and use make_archive
        #output_filename = os.path.join(zip_folder, zip_filename)
        #make_archive(folder_to_zip, output_filename)
        zip_files(zip_filename, output_files, zip_folder)

        # URL to the resource
        url = request.host_url +"distribution/download/" + zip_folder_id

        # send email if email address
        if email_address:
            log.info("sending email to: %s" % email_address)
            html = email_body.replace("{{LINK}}", url)
            print email_user
            print email_address
            print email_password
            email_utils.send_email(email_user, email_address, email_password, email_header, html)

        return Response(json.dumps('{ "url" : "' + url + '"}'), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/vectors/spatial_query/', methods=['POST'])
@app.route('/vectors/spatial_query', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_layers_vectors_spatial_query():
    try:
        # TODO: Not implemented yet!!!!
        #
        # stats = Stats(settings)
        # db_spatial = stats.db_spatial
        # # TODO: it should be a Thread
        #
        # user_json = request.get_json()
        # uids = user_json["vector"]["uids"]
        # email_address = None if "email_address" not in user_json else user_json["email_address"]
        #
        # # create a random tmp folder
        # zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        # zip_folder = os.path.join(distribution_folder, zip_folder_id)
        # os.mkdir(zip_folder)
        #
        # # create a valid folder name to zip it
        # output_folder = os.path.join(zip_folder, "layers")
        # os.mkdir(output_folder)
        #
        # output_files = []
        # for uid in uids:
        #     # export whole shapefile
        #
        #     # get uid (TODO: contains already the table id or call the metadata?)
        #
        #     # for now the shapefile with be the whole shapefile without cutting it
        #
        #     # move file to distribution tmp folder
        #
        #     # path, filename, name = get_filename(filepath, True)
        #     # dst_file = os.path.join(output_folder, filename)
        #     # #dst_file = tmp_folder
        #     #
        #     # log.info(filepath)
        #     # log.info(dst_file)
        #     # move(filepath, dst_file)
        #     #
        #     # # rename file based on uid layer_name (i.e. fenix:trmm_08_2014 -> trmm_08_2014)
        #     output_filename = uid.split(":")[1] + ".geotiff"
        #      output_file = os.path.join(output_folder, output_filename)
        #     # os.rename(dst_file, output_file)
        #
        #     # saving the output file to zip
        #     output_files.append(output_file)
        #
        # # zip folder or files
        # zip_files(zip_filename, output_files, zip_folder )
        #
        # # URL to the resource
        # url = request.host_url +"distribution/download/" + zip_folder_id
        #
        # # send email if email address
        # if email_address:
        #     log.info("sending email to: %s" % email_address)
        #     html = email_body.replace("{{LINK}}", url)
        #     print email_user
        #     print email_address
        #     print email_password
        #     email_utils.send_email(email_user, email_address, email_password, email_header, html)
        #return Response(json.dumps('{ "url" : "' + url + '"}'), content_type='application/json; charset=utf-8')
        return Response(json.dumps({}), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



#http://localhost:5005/distribution/raster/fenix:trmm_06_2014;fenix:trmm_07_2014;fenix:trmm_08_2014;fenix:rice_area1;fenix:apple_area1;fenix:banana_area1/spatial_query/{ "vector" : { "query_extent" : "SELECT ST_AsGeoJSON(ST_Extent(geom)) FROM {{SCHEMA}}.gaul0_3857_test WHERE adm0_name IN ('Spain', 'Italy', 'Germany','China')", "query_layer" : "SELECT * FROM {{SCHEMA}}.gaul0_3857_test WHERE adm0_name IN ('Spain', 'Italy', 'Germany','China')"}}
#http://localhost:5005/distribution/raster/fenix:MODIS_brazil_korea/spatial_query/%7B%20%22vector%22%20:%20%7B%20%22query_extent%22%20:%20%22SELECT%20ST_AsGeoJSON%28ST_Transform%28ST_SetSRID%28ST_Extent%28geom%29,%203857%29,%20%7B%7BSRID%7D%7D%29%29%20FROM%20%7B%7BSCHEMA%7D%7D.gaul0_3857_test%20WHERE%20adm0_name%20IN%20%28%27Brazil%27%29%22,%20%22query_layer%22%20:%20%22SELECT%20*%20FROM%20%7B%7BSCHEMA%7D%7D.gaul0_3857_test%20WHERE%20adm0_name%20IN%20%28%27Brazil%27%29%22%7D%7D
@app.route('/raster/<uids>/spatial_query/<spatial_query>/', methods=['GET'])
@app.route('/raster/<uids>/spatial_query/<spatial_query>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_layers(uids, spatial_query):
    try:
        stats = Stats(settings)
        db_spatial = stats.db_spatial

        log.info(uids)
        log.info(spatial_query)
        uids = uids.split(",")
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

            authority_name, authority_code  = get_authority(raster_path)
            log.info(db_spatial.schema)
            log.info(authority_name)
            log.info(authority_code)


            query_extent = json_filter["vector"]["query_extent"]
            query_layer = json_filter["vector"]["query_layer"]

            query_extent = query_extent.replace("{{SCHEMA}}", db_spatial.schema)
            query_extent = query_extent.replace("{{SRID}}", authority_code)
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
        # if email_address:
        #     log.info("sending email to: %s" % email_address)
        #     html = email_body.replace("{{LINK}}", url)
        #     email_utils.send_email(email_user, email_address, email_password, email_header, html)

        url = request.host_url +"distribution/download/" + zip_folder_id
        return Response(json.dumps('{ "url" : "'+ url + '"}'), content_type='application/json; charset=utf-8')
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/download/<id>/', methods=['GET'])
@app.route('/download/<id>', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_zip_file(id):
    try:
        log.info(request.base_url)
        log.info(request.path)
        log.info(distribution_folder + str(id) + "/" + zip_filename)
        return send_from_directory(directory=distribution_folder + str(id), filename=zip_filename + ".zip",  as_attachment=True, attachment_filename=zip_filename)
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/downloadraster2/', methods=['GET'])
@app.route('/downloadraster2', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_raster_file2():
    try:
        payload = request.get_json()
        log.info(request.base_url)
        log.info(request.path)
        # log.info(distribution_folder + str(id) +"/" + zip_filename)
        dir_name = payload[0:payload.index('final.tif')]
        return send_from_directory(directory=dir_name, filename=zip_filename,  as_attachment=True, attachment_filename="layer.geotiff")
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())

@app.route('/downloadraster/<path>', methods=['GET'])
@app.route('/downloadraster/<path>/', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def get_raster_file(path):
    try:
        path = path.replace(':', '/')
        log.info(path)
        dir_name = path[0:path.rindex('/')]
        log.info(dir_name)
        return send_from_directory(directory=dir_name, filename="final.tif",  as_attachment=True, attachment_filename="layer.geotiff")
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())


@app.route('/download/raster/<uid>', methods=['GET'])
@app.route('/download/raster/<uid>/', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def download_raster_file(uid):
    try:
        stats = Stats(settings)
        log.info(uid)
        path = stats.get_raster_path(uid)
        print path
        dir_name = path[0:path.rindex('/')]
        print dir_name
        filename = get_filename(dir_name)
        return send_from_directory(directory=dir_name, filename=filename + ".geotiff",  as_attachment=True, attachment_filename=filename + ".tif")
    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())



@app.route('/download/vectors/<uids>', methods=['GET'])
@app.route('/download/vectors/<uids>/', methods=['GET'])
@cross_origin(origins='*', headers=['Content-Type'])
def download_vectors_files(uids):
    try:
        uids = uids.split(",")

        # create a random tmp folder
        zip_folder_id = str(uuid.uuid4()).encode("utf-8")
        zip_folder = os.path.join(distribution_folder, zip_folder_id)
        os.mkdir(zip_folder)

        # create a valid folder name to zip it
        output_folder = os.path.join(zip_folder, "layers")
        os.mkdir(output_folder)

        # parsing the uids
        output_folders = []
        stats = Stats(settings)
        datasource = stats.db_spatial.datasource
        tablenames = []
        filenames = []
        for uid in uids:
            layername = uid.split(":")[1]
            filenames.append(layername)
            tablenames.append(datasource["schema"] + "." + layername if "schema" in datasource else layername)


        # TODO: call the metadata DSD to get right table?
        folder_to_zip = create_shapefiles_from_postgis_tables(datasource, tablenames, filenames)

        # zip folder or files
        output_filename = os.path.join(zip_folder, zip_filename)
        make_archive(folder_to_zip, output_filename)

        # URL to the resource
        url = request.host_url + "distribution/download/" + zip_folder_id

        # send email if email address
        # if email_address:
        #     log.info("sending email to: %s" % email_address)
        #     html = email_body.replace("{{LINK}}", url)
        #     print email_user
        #     print email_address
        #     print email_password
        #     email_utils.send_email(email_user, email_address, email_password, email_header, html)

        return Response(json.dumps('{ "url" : "' + url + '"}'), content_type='application/json; charset=utf-8')



    except PGeoException, e:
        raise PGeoException(e.get_message(), e.get_status_code())