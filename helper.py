import requests
import json
import os
import time
from datetime import datetime
import argparse
import tnnhelper


parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store_true', default=False, dest='configmode', help='Run in configuration mode')

myargs = parser.parse_args()

if myargs.configmode:
	print("Config Mode!")


tnnhelper = tnnhelper.tnnhelper()
tnnhelper.get_nodes()
#tnnhelper.create_link("db0luh")
tnnhelper.get_links()
tnnhelper.config_save()
