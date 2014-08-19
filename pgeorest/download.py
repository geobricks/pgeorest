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


download = Blueprint('download', __name__)
thread_manager_processes = {}
progress_map = {}
threads_map_key = 'FENIX'


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



# @download.route('/start/<source_name>/<product>/<year>/<day>/<layer_name>')
# @cross_origin(origins='*')
# def process_start(source_name, product, year, day, layer_name):
#     fjp = LayerDownloadThread(source_name, product, year, day, layer_name)
#     fjp.start()
#     if not threads_map_key in thread_manager_processes:
#         thread_manager_processes[threads_map_key] = {}
#     thread_manager_processes[threads_map_key][layer_name] = fjp
#     percent_done = round(fjp.percent_done(), 1)
#     done = False
#     return jsonify(key=layer_name, percent=percent_done, done=done)
#
#
# @download.route('/progress/<layer_name>')
# @cross_origin(origins='*')
# def process_progress(layer_name):
#     if layer_name not in progress_map:
#         progress = {'download_size': 'unknown', 'layer_name': 'unknown', 'progress': 0, 'total_size': 'unknown', 'status': 'unknown'}
#         return jsonify(progress=progress)
#     return jsonify(progress=progress_map[layer_name])
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