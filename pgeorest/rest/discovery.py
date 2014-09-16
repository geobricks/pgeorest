from ftplib import FTP
import json
from flask import Blueprint
from flask import Response
from flask.ext.cors import cross_origin
from pgeorest.utils import read_config_file_json
from pgeo.error.custom_exceptions import PGeoException
from pgeo.error.custom_exceptions import errors
from pgeo.dataproviders import trmm1 as t


discovery = Blueprint('discovery', __name__)


