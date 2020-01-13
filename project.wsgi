#!usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/App/itemCatalog/")

from __init__ import app as application
