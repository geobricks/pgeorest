from flask import Blueprint
from flask import jsonify
from flask.ext.cors import cross_origin
from pgeo.thread.download_threads_manager import LayerDownloadThread
from pgeo.thread.download_threads_manager import Manager
from pgeo.config.settings import read_config_file_json
from ftplib import FTP
from pgeo.utils.filesystem import create_filesystem


download = Blueprint('download', __name__)
thread_manager_processes = {}
progress_map = {}
threads_map_key = 'FENIX'


@download.route('/')
def index():
    return 'Welcome to the Download module!'

# TODO: alter to pass the list of layers to be downloaded, taken from browse service
@download.route('/start/manager/<source_name>/<product>/<year>/<day>')
@cross_origin(origins='*')
def manager_start(source_name, product, year, day):
    create_filesystem(source_name, {'product': 'Simone', 'year': '2014', 'day': '1'})
    manager = Manager(source_name, product, year, day)
    manager.run()
    conf = read_config_file_json(source_name, 'data_providers')
    ftp = FTP(conf['source']['ftp']['base_url'])
    ftp.login()
    ftp.cwd(conf['source']['ftp']['data_dir'])
    ftp.cwd(product)
    ftp.cwd(year)
    ftp.cwd(day)
    output = []
    ftp_list = ftp.nlst()
    ftp.quit()
    for layer_name in ftp_list:
        output.append(layer_name)
    return jsonify(layers=output)


@download.route('/start/<source_name>/<product>/<year>/<day>/<layer_name>')
@cross_origin(origins='*')
def process_start(source_name, product, year, day, layer_name):
    fjp = LayerDownloadThread(source_name, product, year, day, layer_name)
    fjp.start()
    if not threads_map_key in thread_manager_processes:
        thread_manager_processes[threads_map_key] = {}
    thread_manager_processes[threads_map_key][layer_name] = fjp
    percent_done = round(fjp.percent_done(), 1)
    done = False
    return jsonify(key=layer_name, percent=percent_done, done=done)


@download.route('/progress/<layer_name>')
@cross_origin(origins='*')
def process_progress(layer_name):
    if layer_name not in progress_map:
        progress = {'download_size': 'unknown', 'layer_name': 'unknown', 'progress': 0, 'total_size': 'unknown', 'status': 'unknown'}
        return jsonify(progress=progress)
    return jsonify(progress=progress_map[layer_name])


@download.route('/kill/<key>')
@cross_origin(origins='*')
def kill(key):
    percent_done = thread_manager_processes[threads_map_key][key].percent_done()
    del thread_manager_processes[threads_map_key][key]
    done = True
    percent_done = round(percent_done, 1)
    return jsonify(key=key, percent=percent_done, done=done)