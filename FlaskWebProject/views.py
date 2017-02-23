from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo
from os import environ


app.config['MONGO_URI'] = "mongodb://isiemphours:3A9cNCEUYSK6Ut7lP8HHVCx8bvKJPnTnmgCnU8VsYhb5w5T9etfxdPorxYHj17kYnh74dtLl7709M3T8uV4C1Q==@isiemphours.documents.azure.com:10250/people?ssl=true&ssl_cert_reqs=CERT_NONE"


mongo = PyMongo(app, config_prefix='MONGO')

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('EmployeeID', required=True, help='Employee ID is required', type=int)
parser.add_argument('firstname')
parser.add_argument('lastname')
parser.add_argument('SupervisorName')
parser.add_argument('SupervisorID', required=True, help='Supervisor ID is required', type=int)
parser.add_argument('role')
parser.add_argument('active', default=True, type=bool)
parser.add_argument('hours', type=list, location='json')


putParser = parser.copy()
putParser.replace_argument('hours', location='json', type=dict)


class People(Resource):

    def get(self, EmployeeID=None, SupervisorID=None):

        if EmployeeID:
            employee_info = mongo.db.employee.find_one({'EmployeeID': int(EmployeeID)})
            if employee_info:
                return str(employee_info)
            else:
                return {'Error': 'no employee found for:' + str(EmployeeID)}

        elif SupervisorID:
            employees = mongo.db.employee
            emps = []
            for employee in employees.find({'SupervisorID': int(SupervisorID)}):
                emps.append(employee)
            if len(emps) == 0:
                return {'Error': 'No employees found for ' + str(SupervisorID)}
            else:
                return str(emps)

        else:
            employees = mongo.db.employee
            emps = []
            for employee in employees.find():
                emps.append(employee)
        return str(emps)

    def post(self):
        data = parser.parse_args()
        if not data:
            data = {'response': 'ERROR'}
            return jsonify(data)
        else:
            EmployeeID = data.get('EmployeeID')
            if EmployeeID:
                if mongo.db.employee.find_one({'EmployeeID': EmployeeID}):
                    return {'response': 'Employee already exists'}
                else:
                    mongo.db.employee.insert_one(data)
                    return {'success': 'employee ' + str(EmployeeID) + ' created'}
            elif type(data) == list:
                mongo.db.employee.insert(data)
                return {'Created': str(len(data))+' Employees'}
            else:
                return {'response': 'Employee ID missing'}

    def delete(self, EmployeeID):
        if EmployeeID:
            if mongo.db.employee.find_one({'EmployeeID': int(EmployeeID)}):
                mongo.db.employee.remove({'EmployeeID': int(EmployeeID)})
                return {'success': 'employee' + str(EmployeeID) + ' deleted'}
            else:
                return {'employee ' + str(EmployeeID): 'not found'}
        else:
            return {'Error': 'Delete Failed No Employee ID'}

    def put(self):
        data = putParser.parse_args()
        EmployeeID = data.get('EmployeeID')
        if not data:
            data = {'ERROR': 'No Data'}
            return jsonify(data)
        else:
            if EmployeeID:
                if mongo.db.employee.find_one({'EmployeeID': int(EmployeeID)}):
                    # Needs fixing can't add dict to list
                    mongo.db.employee.update_one({'EmployeeID': int(EmployeeID)}, {'$addToSet': {"hours": data.get('hours')}})

                    return {'response': 'Employee:'+str(EmployeeID)+' updated'}
                else:
                    return {'Error': 'employee ' + str(EmployeeID) + ' not found'}

            else:
                return {'response': 'Employee ID missing'}


api.add_resource(People, '/api/people')
api.add_resource(People, '/api/people/<EmployeeID>', endpoint='employee')
api.add_resource(People, '/api/people/super/<SupervisorID>', endpoint='supervisor')


if __name__ == '__main__':
    app.run()
