#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/")

from FlaskApp import app as application
sys.path.append('/var/www/FlaskApp/FlaskApp/venv/lib/python3.8/site-packages')
