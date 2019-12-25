import sys
from flask import Flask, request, Blueprint, jsonify
from flask_restplus import Api, Resource, fields, reqparse, Namespace
from flask_jwt_extended import jwt_required, get_raw_jwt, get_jwt_identity, get_jwt_claims
from core import users, familyinfo, response , utils
from .users import jwt_parser,forgot_password_model

family_info = Namespace('FamilyInformation', description='Family Relationships Operations')

add_primary_secondary_model = family_info.model('AddPrimarySecondaryUserFields', {
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
}) 

primary_secondary_list_fields = family_info.model('PrimarySecondaryListFields', {
    "iRelationID": fields.Integer(example=200),    
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
}) 

add_primary_response_model = family_info.model('AddPrimarySecondaryResponse',{
    "responseMessage": fields.String(example="Primary User Added Successfully"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_primary_secondary_model)
})


primary_list_response_model = family_info.model('PrimaryListResponse',{
    "responseMessage": fields.String(example="Primary Users List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(primary_secondary_list_fields))
})


add_secondary_response_model = family_info.model('AddSecondaryResponse',{
    "responseMessage": fields.String(example="Secondary User Added Successfully"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_primary_secondary_model)
})
edit_secondary_response_model = family_info.model('EditSecondaryResponse',{
    "responseMessage": fields.String(example="Secondary User Updated Successfully"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_primary_secondary_model)
})
edit_primary_response_model = family_info.model('EditPrimaryResponse',{
    "responseMessage": fields.String(example="Primary User Updated Successfully"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_primary_secondary_model)
})
secondary_list_response_model = family_info.model('SecondaryListResponse',{
    "responseMessage": fields.String(example="Secondary Users List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(primary_secondary_list_fields))
})
remove_primary_response_model = family_info.model('SecondaryListResponse',{
    "responseMessage": fields.String(example="Primary User Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(forgot_password_model)
})
remove_secondary_response_model = family_info.model('SecondaryListResponse',{
    "responseMessage": fields.String(example="Secondary User Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(forgot_password_model)
})

add_member_model = family_info.model('AddMemberFields',{
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'vRelation':fields.String(example="Son"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1)
})
add_member_response_model = family_info.model('AddMemberResponse',{
    "responseMessage": fields.String(example="Family Member Added"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_member_model)
})


user_model = family_info.model('UserFields', {
    "PK": fields.Integer(example=200),    
    'vFullName':fields.String(example="John Doe"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
}) 


family_member_model = family_info.model('FamilyMemberFields', {
    'iFamMemID': fields.Integer(example=200),        
    'vFullName':fields.String(example="John Doe"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'vRelation':fields.String(example="Son"),    
    'PrimaryCount' : fields.Integer(example=1),
    'SecondaryCount' : fields.Integer(example=2),
    'AddedBy' : fields.String(example="test")
})

get_family_info_model = family_info.model('GetFamilyInfoFields',{
    'User': fields.Nested(user_model),
    'PrimaryMembers' : fields.List(fields.Nested(user_model)),
    'FamilyMembers' : fields.List(fields.Nested(family_member_model)),
    'SecondaryFor' : fields.List(fields.Nested(user_model))
})
get_family_info_response_model = family_info.model('GetFamilyInfoResponse',{
    "responseMessage": fields.String(example="Family Information"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(get_family_info_model)
})

edit_member_model = family_info.model('EditMemberFields', {
    'iFamMemID': fields.Integer(example=200),            
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
    'vRelation':fields.String(example="Son"),
}) 
edit_member_response_model = family_info.model('EditMemberResponse',{
    "responseMessage": fields.String(example="Family Member Updated"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(edit_member_model)
})

remove_member_model = family_info.model('RemoveMemberFields', {
    'iFamMemID': fields.Integer(example=20)
})
remove_member_response_model = family_info.model('RemoveMemberResponse',{
    "responseMessage": fields.String(example="Family Member Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(remove_member_model)
})

assign_primary_secondary_model = family_info.model('AssignPrimaryFields',{
    "responseMessage": fields.String(example="Family Member Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(edit_member_model)
})


@family_info.route("/AddPrimary")
class AddPrimary(Resource):
    @family_info.marshal_with(add_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Add Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.add_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=1)
        # except:
        # 	return response.send_response(500,"Something went wrong",None)

@family_info.route("/PrimaryList")
class PrimaryList(Resource):
    @family_info.marshal_with(primary_list_response_model, code=200)
    @family_info.expect(jwt_parser)
    @jwt_required    
    def get(self):
        """
        View Primary List
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return familyinfo.primary_secondary_list(iUserID,vDeviceUniqueID,tiRelationType=1)

@family_info.route("/SecondaryList")
class SecondaryList(Resource):
    @family_info.marshal_with(secondary_list_response_model, code=200)
    @family_info.expect(jwt_parser)
    @jwt_required    
    def get(self):
        """
        View Secondary List
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return familyinfo.primary_secondary_list(iUserID,vDeviceUniqueID,tiRelationType=2)


@family_info.route("/AddSecondary")
class AddSecondary(Resource):
    @family_info.marshal_with(add_secondary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Add Secondary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.add_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=2)
        # except:
        #   return response.send_response(500,"Something went wrong",None)


@family_info.route("/EditPrimary")
class EditPrimary(Resource):
    @family_info.marshal_with(edit_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Edit Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.edit_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=1)



@family_info.route("/EditSecondary")
class EditSecondary(Resource):
    @family_info.marshal_with(edit_secondary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Edit Secondary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.edit_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=2)


@family_info.route("/RemovePrimary")
class RemovePrimary(Resource):
    @family_info.marshal_with(remove_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=forgot_password_model)
    @jwt_required    
    def post(self):
        """
        Remove Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.remove_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=1)


@family_info.route("/RemoveSecondary")
class RemoveSecondary(Resource):
    @family_info.marshal_with(remove_secondary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=forgot_password_model)
    @jwt_required    
    def post(self):
        """
        Remove Secondary User
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.remove_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=2)

@family_info.route("/AddFamilyMember")
class AddFamilyMember(Resource):
    @family_info.marshal_with(add_member_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=add_member_model)
    @jwt_required    
    def post(self):
        """
        Add Family Member
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.add_family_member(data,iUserID,vDeviceUniqueID)
        # except:
        #   return response.send_response(500,"Something went wrong",None)

@family_info.route("/GetFamilyInformation")
class GetFamilyInformation(Resource):
    @family_info.marshal_with(get_family_info_response_model, code=200)
    @family_info.doc(parser=jwt_parser)
    @jwt_required    
    def get(self):
        """
        Get Family Information 
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return familyinfo.get_family_info(iUserID,vDeviceUniqueID)

@family_info.route("/EditFamilyMember")
class EditFamilyMember(Resource):
    @family_info.marshal_with(edit_member_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=edit_member_model)
    @jwt_required    
    def post(self):
        """
        Edit Family Member
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.edit_family_member(data,iUserID,vDeviceUniqueID)


@family_info.route("/RemoveFamilyMember")
class RemoveFamilyMember(Resource):
    @family_info.marshal_with(remove_member_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=remove_member_model)
    @jwt_required    
    def post(self):
        """
        Remove Family Member
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.remove_family_member(data,iUserID,vDeviceUniqueID)

# @family_info.route("/AssignPrimary")
# class RemoveFamilyMember(Resource):
#     @family_info.marshal_with(assign_primary_response_model, code=200)
#     @family_info.doc(parser=jwt_parser,body=assign_primary_model)
#     @jwt_required    
#     def post(self):
#         """
#         Assign Primary User
#         """
#         # try:
#         iUserID = get_jwt_identity()
#         vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
#         data = request.json
#         return familyinfo.remove_family_member(data,iUserID,vDeviceUniqueID)
