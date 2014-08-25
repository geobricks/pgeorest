import json
from flask import Blueprint
from flask import jsonify
from flask.ext.cors import cross_origin
from flask import request
from flask import Response
from pgeo.error.custom_exceptions import PGeoException
from pgeo.thread.download_threads_manager import Manager
from pgeo.thread.download_threads_manager import progress_map
from pgeo.thread.download_threads_manager import out_template
from pgeo.gis.raster import process_hdfs
from pgeo.config.settings import read_config_file_json


download = Blueprint('download', __name__)


@download.route('/')
def index():
    return 'Welcome to the Download module!'


@download.route('/<source_name>', methods=['POST'])
@download.route('/<source_name>/', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def manager_start(source_name):
    try:
        payload = request.get_json()
        file_paths_and_sizes = payload['file_paths_and_sizes']
        filesystem_structure = payload['filesystem_structure']
        mgr = Manager(source_name, file_paths_and_sizes, filesystem_structure)
        target_dir = mgr.run()
        out = {'source_path': target_dir}
        return Response(json.dumps(out), content_type='application/json; charset=utf-8')
    except Exception, e:
        raise PGeoException(e.message, 500)


@download.route('/progress/<layer_name>')
@download.route('/progress/<layer_name>/')
@cross_origin(origins='*')
def progress(layer_name):
    if layer_name not in progress_map:
        return jsonify(progress=out_template)
    return jsonify(progress_map[layer_name])


@download.route('/process/<source_name>', methods=['POST'])
@download.route('/process/<source_name>/', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def process_rasters_service(source_name):
    try:
        payload = request.get_json()
        conf = read_config_file_json(source_name, 'data_providers')
        obj = conf['processing']
        obj['source_path'] = payload['source_path']
        obj['output_path'] = payload['source_path'] + '/OUTPUT'
        obj['gdalwarp']['-tr'] = str(payload['pixel_size']) + ', -' + str(payload['pixel_size'])
        print obj
        # print payload['source_path']
        # print payload['pixel_size']
        # obj = {
        #     "output_file_name" : "MODIS_250m.tif",
        #     "source_path" : payload['source_path'],
        #     "band" : 1,
        #     "output_path" : payload['source_path'] + "/OUTPUT",
        #     "gdal_merge" : {
        #         # "-n" : -3000,
        #         # "-a_nodata" : -3000
        #     },
        #     "gdalwarp" : {
        #         "-multi" : "",
        #         "-of" : "GTiff",
        #         "-tr" : "0.004166665, -0.004166665",
        #         "-s_srs" :"'+proj=sinu +R=6371007.181 +nadgrids=@null +wktext'",
        #         "-co" : "'TILED=YES'",
        #         "-t_srs" : "EPSG:4326",
        #         "-srcnodata" : -3000,
        #         "-dstnodata" : "nodata"
        #     },
        #     "gdaladdo" : {
        #         "parameters" : {
        #             "-r" : "average"
        #         },
        #         "overviews_levels" : "2 4 8 16"
        #     }
        # }
        try:
            process_hdfs(obj)
            return Response(json.dumps('{"OK":"OK"}'), content_type='application/json; charset=utf-8')
        except Exception, e:
            print e
            raise PGeoException(e.message, 500)
    except Exception, e:
        print e
        raise PGeoException(e.message, 500)