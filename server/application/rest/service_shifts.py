"""
This module handles service shift operations.
"""
from flask import Blueprint, request, Response
from flask_cors import cross_origin
from use_cases.add_service_shifts import shift_add_use_case
from use_cases.list_service_shifts_use_case import service_shifts_list_use_case
from repository.mongo.service_shifts import ServiceShiftsMongoRepo
from domains.service_shift import ServiceShift
from application.rest.work_shift import db_configuration
from application.rest.work_shift import HTTP_STATUS_CODES_MAPPING
from responses import ResponseTypes
from serializers.service_shift import ServiceShiftJsonEncoder
import json

service_shift_bp = Blueprint('service_shift', __name__)

@service_shift_bp.route('/service_shift', methods=['GET', 'POST'])
@cross_origin()
def service_shift():
    """
    Handles POST to add service shift, GET to list all shifts for a shelter.
    """
    db_config = db_configuration()
    repo = ServiceShiftsMongoRepo(db_config[0], db_config[1])
    if request.method == 'GET':
        shifts_as_dict = service_shifts_list_use_case(repo)
        shifts_as_json = [
            json.dumps(service_shift, cls = ServiceShiftJsonEncoder)
            for service_shift in shifts_as_dict
        ]
        return Response(
            shifts_as_json,
            mimetype='application/json',
            status=HTTP_STATUS_CODES_MAPPING[ResponseTypes.SUCCESS]
        )
    elif request.method == 'POST':
        shifts_as_dict = request.get_json()
        print(shifts_as_dict)
        if isinstance(shifts_as_dict, list) and shifts_as_dict:
            shifts_as_dict = shifts_as_dict[0]
        shifts_obj = ServiceShift.from_dict(shifts_as_dict)
        add_response = shift_add_use_case(repo, shifts_obj, 
                                          existing_shifts=[], shelter_id=None)
        status_code = HTTP_STATUS_CODES_MAPPING[ResponseTypes.PARAMETER_ERROR]
        if add_response['success']:
            status_code = HTTP_STATUS_CODES_MAPPING[ResponseTypes.SUCCESS]
        return Response(
            json.dumps(add_response, default=str),
            mimetype = 'application/json',
            status = status_code
        )
