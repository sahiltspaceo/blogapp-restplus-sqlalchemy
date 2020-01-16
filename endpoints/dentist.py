from flask import request
from flask_restplus import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from core import dentist
from .users import jwt_parser


dentist_ns = Namespace('Dentist', description='Dentist Operations')

dentist_model = dentist_ns.model('DentistFields', {
    'iDentistID': fields.String(example="Mjg="),    
    'vDentistName':  fields.String(example="test123"),
    'tOpenTime':fields.String(example='09:00'),
    'tCloseTime':fields.String(example="20:00"),
    'vAddress': fields.String(example="test"),
}) 

dentist_list_response = dentist_ns.model('DentistListResponse',{
    "responseMessage": fields.String(example="Dentist List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(dentist_model)
})

appointment_model = dentist_ns.model('AppointmentFields', {
    'iDentistID': fields.String(example="Mjg="),    
    'iFamMemID': fields.String(example="Mjg="),    
    'dDateOfAppoint':  fields.Date(example="12/12/2018"),
    'tTimeOfAppoint':fields.String(example='09:00')
}) 

appointment_response = dentist_ns.model('AppointmentResponse',{
    "responseMessage": fields.String(example="Appointment Created"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(appointment_model)
})

@dentist_ns.route("/DentistList")
class DentistList(Resource):
    @dentist_ns.marshal_with(dentist_list_response, code=200)
    @dentist_ns.doc(parser=jwt_parser)
    @jwt_required    
    def get(self):
        """
        Dentist List
        """
        iUserID = get_jwt_identity()
        return dentist.dentist_list(iUserID)



@dentist_ns.route("/SetAppointment")
class SetAppointment(Resource):
    @dentist_ns.marshal_with(appointment_response, code=200)
    @dentist_ns.doc(parser=jwt_parser,body=appointment_model)
    @jwt_required    
    def post(self):
        """
        Set Appointment 
        """
        iUserID = get_jwt_identity()
        data = request.json
        return dentist.set_appointment(data,iUserID)

