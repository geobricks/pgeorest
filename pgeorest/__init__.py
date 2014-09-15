from flask import Flask
from flask.ext.cors import CORS
from flask import jsonify
from flask import render_template
from importlib import import_module
from pgeo.error.custom_exceptions import PGeoException
from pgeorest.config.settings import settings
from pgeorest.rest.download import download
from pgeorest.rest.process import processing
from pgeorest.rest.schema import schema
from pgeorest.rest.filesystem import filesystem
from pgeorest.rest.metadata import metadata
from pgeorest.rest.search import search
from pgeorest.rest import stats
from pgeorest.rest import spatialquery
from pgeorest.rest import distribution
from pgeorest.rest import ghg
import logging


# Initialize the Flask app
app = Flask(__name__)


# Initialize CORS filters
cors = CORS(app, resources={r'/*': {'origins': '*'}})


# Custom error handling
@app.errorhandler(PGeoException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Custom 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Root REST
@app.route('/')
def root():
    return 'Welcome to PGeo REST!'


# Dynamic import of modules specified in config.settings.py
for module in settings['modules']:

    # Load module
    mod = import_module(module['module_name'])

    # Load Blueprint
    rest = getattr(mod, module['rest_name'])

    # Register Blueprint
    app.register_blueprint(rest, url_prefix=module['url_prefix'])


# Core services.
app.register_blueprint(download, url_prefix='/download')
app.register_blueprint(schema, url_prefix='/schema')
app.register_blueprint(filesystem, url_prefix='/filesystem')
app.register_blueprint(metadata, url_prefix='/metadata')
app.register_blueprint(search, url_prefix='/search')
app.register_blueprint(stats.app, url_prefix='/stats')
app.register_blueprint(spatialquery.app, url_prefix='/spatialquery')
app.register_blueprint(distribution.app, url_prefix='/distribution')
app.register_blueprint(processing, url_prefix='/process')
app.register_blueprint(ghg.app, url_prefix='/ghg')


links = []
for rule in app.url_map.iter_rules():
    print rule
    print rule.methods
    print rule.arguments
    print


# Logging level.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



# Start Flask server
if __name__ == '__main__':
    app.run(host=settings['host'], port=settings['port'], debug=settings['debug'], threaded=True)


