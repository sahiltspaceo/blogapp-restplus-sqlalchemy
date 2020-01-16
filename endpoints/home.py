from flask import  request
from flask_restplus import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt_claims
from core import home
from .users import jwt_parser,error_response

home_ns = Namespace('Home', description='Home Screen')

pagination_body = home_ns.model('PaginationFields',{
    'ItemsPerPage' : fields.Integer(example=2),
    'PageIndex' : fields.Integer()
})
pagination_model = home_ns.model('Pagination',{
    'AppointmentsPagination' : fields.Nested(pagination_body),  
    'EventsPagination' : fields.Nested(pagination_body)
})
appointment_item_model = home_ns.model('AppointmentItemFields',{
    'vFullName': fields.String(example="John Doe"),
    'vProfilePicURL' : fields.String(),
    'vDentistName':  fields.String(example="Dr Henry"), 
    'tTimeOfAppoint':fields.String(example='09:00')
})

home_appointment_model = home_ns.model('HomeAppointmentFields', {
    'TotalItems' : fields.Integer(example='1'),
    'AppointmentItems': fields.List(fields.Nested(appointment_item_model))
})
home_user_model = home_ns.model('HomeUserFields',{
    'vFullName': fields.String(example="John Doe"),    
    'vProfilePicURL' : fields.String()
})
event_item_model = home_ns.model('EventItemFields', {
    'AddedBy' : fields.String(example="test test"),     
    'vFullName': fields.String(example="John Doe"),    
    'vProfilePicURL' : fields.String(),
    'iToothCategoryID':  fields.Integer(example=2), 
    'tiInput': fields.Integer(example=2),
    'tiEvent': fields.Integer(example=3),
    'tComments' : fields.String(example="Test Comments"),
    'vImageURL' : fields.List(fields.String()),
    'vVideoURL' : fields.List(fields.String()),
    'tsCreatedAt' : fields.String()
})  
home_event_model = home_ns.model('HomeEventFields',{
    'TotalItems' : fields.Integer(example='1'),
    'HomeEventItems': fields.List(fields.Nested(event_item_model))
})


home_screen_model = home_ns.model('HomeScreenFields',{
    'User': fields.Nested(home_user_model),
    'Appointments' : fields.Nested(home_appointment_model),
    'Events' : fields.Nested(home_event_model)
})
home_screen_response_model = home_ns.model('HomeScreenResponse',{
  "responseMessage": fields.String(example="Home Screen"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(home_screen_model)
})

@home_ns.route("/HomeScreen")
class HomeScreen(Resource):
    @home_ns.doc(parser = jwt_parser,body=pagination_model)
    @home_ns.response(200,"Home Screen",home_screen_response_model)
    @home_ns.response(400,"Invalid Paging Params",error_response)
    @jwt_required   
    def post(self):
        """
        Home Screen
        """

        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return home.home_screen(data,iUserID,vDeviceUniqueID)
