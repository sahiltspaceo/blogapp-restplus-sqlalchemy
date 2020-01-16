from flask import  request
from flask_restplus import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_raw_jwt, get_jwt_identity,get_jwt_claims
from core import response , settings
from .users import jwt_parser,forgot_password_model

settings_ns = Namespace('Settings', description='User Settings')


tooth_disease_model = settings_ns.model('ToothDiseasesFields',{
    "vTitle": fields.String(example="Stained Teeth"),
    "tContent": fields.String(example="Content")
})
tooth_diseases_response_model = settings_ns.model('ToothDiseasesResponse',{
    "responseMessage": fields.String(example="Tooth Diseases"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(tooth_disease_model))
})
tooth_gallery_model = settings_ns.model('ToothGalleryFields',{
    'iFamMemID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),
    'vFullName' : fields.String(),
    'vMediaURL' : fields.String(),
    'tsCreatedAt' : fields.String(),
    'vMediaType' : fields.String(example="Video")
})
tooth_gallery_response_model = settings_ns.model('ToothGalleryResponse',{
    "responseMessage": fields.String(example="Tooth Diseases"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(tooth_gallery_model))
})
view_profile_model = settings_ns.model('ViewProfileFields',{
    'vEmail': fields.String(),
    'vFullName' : fields.String(),
    'vCountryCode' : fields.String(),
    'vMobile' : fields.String(),
    'dDOB' : fields.String(),
    'vProfilePicURL' : fields.String()
})
view_profile_response = settings_ns.model('view_profile_model',{
    "responseMessage": fields.String(example="Profile Information"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(view_profile_model))
})

update_profile_response = settings_ns.model('update_profile_model',{
    "responseMessage": fields.String(example="Profile Information Updated"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(view_profile_model))
})

logout_response_model = settings_ns.model('LogoutTokenResponse',{
  "responseMessage": fields.String(example="Logout Successful"),
  "responseCode": fields.Integer(example=200),
})
update_password_model = settings_ns.model('UpdatePasswordFields',{
    'vEmail': fields.String(),
    'vPassword':fields.String(),      
})

update_password_response_model = settings_ns.model('UpdatePasswordResponse',{
  "responseMessage": fields.String(example="Password Updated Successfully"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(forgot_password_model)
})
cms_model = settings_ns.model('CMSFields',{
    'CMS' : fields.String(),
    'Content' : fields.String()
})
cms_response = settings_ns.model('CMSResponseFields',{
  "responseMessage": fields.String(example="CMS Response"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(cms_model)
})

@settings_ns.route("/ToothDiseases")
class ToothDiseases(Resource):
    @settings_ns.marshal_with(tooth_diseases_response_model, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required   
    def get(self):
        """
        Tooth Diseases
        """
        # try:
        iUserID = get_jwt_identity()
        return settings.tooth_disease(iUserID)
        # except:
        # 	return response.send_response(500,"Something went wrong",None)

@settings_ns.route("/ToothGallery")
class ToothGallery(Resource):
    @settings_ns.marshal_with(tooth_gallery_response_model, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required   
    def get(self):
        """
        Tooth Gallery
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return settings.tooth_gallery(iUserID,vDeviceUniqueID)
        # except:
        # 	return response.send_response(500,"Something went wrong",None)

@settings_ns.route("/ViewProfile")
class ViewProfile(Resource):
    @settings_ns.marshal_with(view_profile_response, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required   
    def get(self):
        """
        View Profile 
        """
        iUserID = get_jwt_identity()
        return settings.view_profile(iUserID)


@settings_ns.route("/UpdateProfile")
class UpdateProfile(Resource):
    @settings_ns.marshal_with(update_profile_response, code=200)
    @settings_ns.doc(parser=jwt_parser,body=view_profile_model)
    @jwt_required   
    def put(self):
        """
        Update Profile 
        """
        iUserID = get_jwt_identity()
        data = request.json
        return settings.update_profile(data,iUserID)


@settings_ns.route("/Logout")
class UserLogout(Resource):
    @jwt_required
    @settings_ns.marshal_with(logout_response_model, code=200)    
    @settings_ns.doc(parser=jwt_parser)
    def post(self):
        """
        Logout
        """
        # try:
        iUserID = get_jwt_identity()
        AccessToken = get_raw_jwt()['jti']
        return settings.user_logout(AccessToken,iUserID)
        # except Exception as e:
        #     return response.send_response(409, "Something went wrong", None)


@settings_ns.route("/UpdatePassword")
class UpdatePassword(Resource):
    @settings_ns.marshal_with(update_password_response_model, code=200)    
    @settings_ns.expect(update_password_model)
    def put(self):
        """
        Update Password
        """
        data = request.json
        return settings.update_password(data)


@settings_ns.route("/TermsAndConditions")
class TermsAndConditions(Resource):
    @settings_ns.marshal_with(cms_response, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required    
    def get(self):
        """
        Terms And Conditions 
        """
        iUserID = get_jwt_identity()
        return settings.get_cms(iUserID=iUserID,data="Terms & Conditions")

@settings_ns.route("/AboutUs")
class AboutUs(Resource):
    @settings_ns.marshal_with(cms_response, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required    
    def get(self):
        """
        About Us 
        """
        iUserID = get_jwt_identity()
        return settings.get_cms(iUserID=iUserID,data="About Us")


@settings_ns.route("/Notifications")
class Notifications(Resource):
    @settings_ns.marshal_with(cms_response, code=200)
    @settings_ns.expect(jwt_parser)
    @jwt_required    
    def get(self):
        """
        Notifications  
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return settings.get_tnc(iUserID,vDeviceUniqueID)
