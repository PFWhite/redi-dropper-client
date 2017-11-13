import os
import json
import sys

import yaml

from cappy import API
import MySQLdb

from image_file import ImageFile

with open('dropper.polyjuice.conf.yaml', 'r') as infile:
    config = yaml.load(infile)

polyjuice_root = '/tmp'
redcap_url = ''
token = ''
password = ''
database = ''
host = ''
user = ''

redcap_api = API(token, redcap_url, 'master.yaml')
dropper_connection = MySQLdb.connect(host=host, user=user, passwd=password, db=database)

for root, dirs, files in os.walk(polyjuice_root):
    for path in files:
        data = None
        if '.json' in path:
            with open(os.path.join(root, path), 'r') as infile:
                data = json.load(infile)
        if data:
            data['image_path'] = os.path.join(root, path)
            data['ptid'] = sys.argv[1]
            image = ImageFile(file_path, dropper_connection, redcap_api, **data)

            image.get_event_name()
            image.load_into_dropper_db()

