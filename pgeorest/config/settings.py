import logging
import json
import os


settings = {
    
    "modules": [
        # {
        #     # Label
        #     "label": "MODIS",
        #     # The path to the Python file containing the Blueprint
        #     "module_name": "pgeomodis.rest.modis_rest",
        #     # The name of the Blueprint
        #     "rest_name": "modis",
        #     # The prefix to be used for the Blueprint
        #     "url_prefix": "/browse/modis"
        # }
        # {
        #     # Label
        #     "label": "TRMM",
        #     # The path to the Python file containing the Blueprint
        #     "module_name": "pgeotrmm.rest.trmm_rest",
        #     # The name of the Blueprint
        #     "rest_name": "trmm",
        #     # The prefix to be used for the Blueprint
        #     "url_prefix": "/browse/trmm"
    ],

    # To be used by Flask: DEVELOPMENT ONLY
    "debug": True,

    # Flask host: DEVELOPMENT ONLY
    "host": "168.202.28.214",

    # Flask port: DEVELOPMENT ONLY
    "port": 5020,

    # Default folder root to store layers. Each data provider configuration file specifies the path AFTER this folder.
    "target_root": "/home/Desktop/GIS",

    # Each folder cntains one layer only. This is the default file name for such layers.
    "default_layer_name":  "layer.geotiff",

    # Logging configurations
    "logging": {
        "level": logging.INFO,
        "format": "%(asctime)s | %(levelname)-8s | %(name)-20s | Line: %(lineno)-5d | %(message)s",
        "datefmt": "%d-%m-%Y | %H:%M:%s"
    },

    "email": {
        "settings" : "/home/vortex/Desktop/LAYERS/email.json",
        "user" :  None,
        "password" : None
    },

    # Folders
    "folders": {
        "config": "config/",
        "tmp": "/home/vortex/Desktop/LAYERS/tmp",
        "data_providers": "data_providers/",
        "metadata": "metadata/",
        "stats": "stats/",
        "geoserver": "geoserver/",
        "metadata_templates": "metadata/templates/",
        # used on runtime statistics (for Published layers this is the Geoservers Cluster "datadir")
        "geoserver_datadir": "/home/vortex/programs/SERVERS/tomcat_geoservers/data/",
        #"geoserver_datadir": "/home/vortex/Desktop/LAYERS/GEOSERVER_TEST",

        "distribution": "/home/vortex/Desktop/LAYERS/DISTRIBUTION/"
    },

    # Databases
    "db": {
        "metadata": {
            #"connection": "mongodb://168.202.39.41:27017/",
            "connection": "mongodb://localhost:27017/",
            "database": "metadata",
            "document": {
                "layer": "layer"
            }
        },

        "ghg": {
            "connection": "mongodb://168.202.39.41:27017/",
            #"connection": "mongodb://localhost:27017/",
            "database": "metadata",
            "document": {
                "layer": "layer"
            }
        },

        # Spatial Database
        "spatial": {
            # default_db will search in the dbs["database"] as default option
            "dbname": "fenix",
            "host": "EXLPRFAOSTAT1.ext.fao.org",
            "port": "5432",
            "username": "fenix",
            "password": "Qwaszx",
            "schema": "spatial"
        },

        "stats": {
            "dbname": "fenix",
            "host": "EXLPRFAOSTAT1.ext.fao.org",
            "port": "5432",
            "username": "fenix",
            "password": "Qwaszx",
            "schema": "stats"
        }
    },

    # Geoserver
    "geoserver": {
        "geoserver_master": "http://NO:20100/geoserver/rest",
        #"geoserver_master": "http://168.202.28.214:9090/geoserver/rest",
        "geoserver_slaves": [],
        "username": "fenix",
        "password": "Fenix2014",
        "default_workspace": "fenix",
        # this is used as default datasource to this is a reference to the spatial_db
        # this should be connected with the current spatial db
        # TODO: didn't implemnent it yet
        "default_datastore": "pgeo"
    },

    "geoserver_tmp": {
        "geoserver_master": "http://168.202.28.214:9090/geoserver/rest",
        "geoserver_wms": "http://168.202.28.214:9090/geoserver/wms",
        "geoserver_slaves": [],
        "username": "admin",
        "password": "geoserver",
        "default_workspace": "tmp"
    },

    # Stats
    "stats": {
        "db": {
            "spatial": "spatial",
            "stats": "stats"
        }
    },


    # Metadata
    "metadata": {

    }
    
}


def read_config_file_json(filename, folder=''):
    directory = os.path.dirname(os.path.dirname(__file__))
    filename = filename.lower()
    path = directory + '/' + settings['folders']['config'] + settings['folders'][folder]
    print path
    extension = '' if '.json' in filename else '.json'
    return json.loads(open(path + filename + extension).read())


def read_template(filename):
    try:
        directory = os.path.dirname(os.path.dirname(__file__))
        filename = filename.lower()
        path = os.path.join(directory, settings['folders']['config'], settings['folders']['metadata_templates'])
        extension = '' if '.json' in filename else '.json'
        return json.loads(open(path + filename + extension).read())
    except Exception, e:
        print e


def set_email_settings():
    if os.path.isfile(settings["email"]["settings"]):
        settings["email"] = json.loads(open(settings["email"]["settings"]).read())

set_email_settings()