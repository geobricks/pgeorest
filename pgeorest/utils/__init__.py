import json
import os


def read_config_file_json(filename):
    directory = os.path.dirname(os.path.dirname(__file__))
    filename = filename.lower()
    path = directory + '/config/'
    extension = '' if '.json' in filename else '.json'
    return json.loads(open(path + filename + extension).read())