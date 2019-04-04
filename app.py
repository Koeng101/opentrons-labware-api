from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields
from flask.views import MethodView

import glob
import json

from config import DEFINITIONS2

# Init app
app = Flask(__name__)
api = Api(app, version='1.0', title='OpenTrons labware anywhere',
            description='This is an api endpoint to get opentrons labware jsons anywhere',
            )

def open_json(file):
    with open(file) as f:
        json_file = json.load(f)
    return json_file

labwares = {}
for json_file in glob.glob('{}*.json'.format(DEFINITIONS2)):
    labwares[open_json(json_file)['parameters']['loadName']] = json_file

ns = api.namespace('labware', description='OpenTrons labware')
@ns.route('/')
class AllLabware(Resource):
    '''Shares all currently available labware'''
    @ns.doc('labware_list')
    def get(self):
        '''Lists all labware'''
        data = []
        for k,v in labwares.items():
            data.append(open_json(v))
        return jsonify(data)

@ns.route('/<labware>')
class SpecificLabware(Resource):
    '''Shares a specific labware'''
    @ns.doc('labware_get')
    def get(self,labware):
        '''Returns a specific labware definition'''
        return jsonify(open_json(labwares[labware]))




if __name__ == "__main__":
    app.run(host='0.0.0.0')
