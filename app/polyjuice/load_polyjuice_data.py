import os
import json

import yaml

from cappy import API
import MySQLdb

from image_file import ImageFile


polyjuice_root = '/tmp'
redcap_url = ''
token = ''
password = ''
database = ''
host = ''
user = ''

redcap_api = API(token, redcap_url, 'master.yaml')
dropper_connection = MySQLdb.connect(host=host, user=user, passwd=password, db=database)

def is_image_metadata(path):
    """
    There may be a different identifier for the data
    """
    return 'metadata' in path

def load_file(myfile):
    """
    The data may not come back as json
    regardless, it needs to be a dictionary like thing at the then of the day
    """
    return json.load(infile)

for root, dirs, files in os.walk(polyjuice_root):
    for path in files:
        data = None
        if is_image_metadata(path):
            with open(os.path.join(root, path), 'r') as infile:
                data = load_file(infile)
        if data:
            data['image_path']
            image = ImageFile(file_path, dropper_connection, redcap_api, **data)

            image.get_event_name()
            image.load_into_dropper_db()

