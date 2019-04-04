from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
from flask.views import MethodView

import glob
import json

from config import DEFINITIONS2, DEV

from Protocols import transformation
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

#
# Labware
#

ns_labware = api.namespace('labware', description='OpenTrons labware')
@ns_labware.route('/')
class AllLabware(Resource):
    '''Shares all currently available labware'''
    @ns_labware.doc('labware_list')
    def get(self):
        '''Lists all labware'''
        data = []
        for k,v in labwares.items():
            data.append(open_json(v))
        return jsonify(data)

@ns_labware.route('/<labware>')
class SpecificLabware(Resource):
    '''Shares a specific labware'''
    @ns_labware.doc('labware_get')
    def get(self,labware):
        '''Returns a specific labware definition'''
        return jsonify(open_json(labwares[labware]))

#
# Protocols
# 

ns_protocols = api.namespace('protocols', description='Autogenerated protocols')
transformation_model = api.model("transformation", {
    "robot": fields.Raw(),
    "plate": fields.Raw(),
    })

@ns_protocols.route('/transformation')
class TransformationRoute(Resource):
    @ns_protocols.doc('transformation')
    @api.expect(transformation_model)
    def post(self):
        robot = request.get_json()['robot']
        plate = request.get_json()['plate']
        if plate['plate_type'] not in ['miniprep','dna']:
            return jsonify({'message': 'Not raw DNA'},400)
        return jsonify(transformation.transformation(robot,plate))


if __name__ == '__main__' and DEV == True:
    app.run(debug=True)
elif __name__ == '__main__' and DEV == False:
    app.run(host='0.0.0.0')

