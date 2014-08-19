import json
from flask import Blueprint
from flask import jsonify
from flask.ext.cors import cross_origin
from flask import request
from flask import Response
from pgeo.thread.download_threads_manager import LayerDownloadThread
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.thread.download_threads_manager import Manager
from pgeo.thread.download_threads_manager import progress_map


download = Blueprint('download', __name__)
# thread_manager_processes = {}
# progress_map = {}
# threads_map_key = 'FENIX'


@download.route('/')
def index():
    return 'Welcome to the Download module!'

@download.route('/<source_name>', methods=['POST'])
@download.route('/<source_name>/', methods=['POST'])
@cross_origin(origins='*', headers=['Content-Type'])
def manager_start(source_name):
    try:
        file_paths_and_sizes = request.get_json()
        mgr = Manager(source_name, file_paths_and_sizes)
        mgr.run()
        return Response(json.dumps('Manager started.'), content_type='application/json; charset=utf-8')
    except Exception, e:
        raise PGeoException(e.message, 500)


@download.route('/progress/<layer_name>')
@download.route('/progress/<layer_name>/')
@cross_origin(origins='*')
def progress(layer_name):
    if layer_name not in progress_map:
        out = {
            'download_size': 'unknown',
            'layer_name': 'unknown',
            'progress': 0,
            'total_size': 'unknown',
            'status': 'unknown'
        }
        return jsonify(progress=out)
    return jsonify(progress=progress_map[layer_name])




#
#
# @download.route('/kill/<key>')
# @cross_origin(origins='*')
# def kill(key):
#     percent_done = thread_manager_processes[threads_map_key][key].percent_done()
#     del thread_manager_processes[threads_map_key][key]
#     done = True
#     percent_done = round(percent_done, 1)
#     return jsonify(key=key, percent=percent_done, done=done)