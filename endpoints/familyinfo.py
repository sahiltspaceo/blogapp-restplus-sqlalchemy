from flask import request
from flask_restplus import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from core import familyinfo, response,home
from .users import jwt_parser,error_response
from .home import event_item_model
family_info = Namespace('FamilyInformation', description='Family Relationships Operations')

add_primary_secondary_model = family_info.model('AddPrimarySecondaryUserFields', {
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
}) 

primary_secondary_list_fields = family_info.model('PrimarySecondaryListFields', {
    'iRelationID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),    
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vFullName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
})
edit_primary_secondary_fields = family_info.model('EditPrimarySecondaryFields', {
    'iRelationID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),    
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1)
}) 
relation_id_model = family_info.model('RelationIDField', {
    'iRelationID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),
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
    "responseData": fields.Nested(edit_primary_secondary_fields)
})
edit_primary_response_model = family_info.model('EditPrimaryResponse',{
    "responseMessage": fields.String(example="Primary User Updated Successfully"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(edit_primary_secondary_fields)
})
secondary_list_response_model = family_info.model('SecondaryListResponse',{
    "responseMessage": fields.String(example="Secondary Users List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(primary_secondary_list_fields))
})
remove_primary_response_model = family_info.model('RemovePrimaryResponse',{
    "responseMessage": fields.String(example="Primary User Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(relation_id_model)
})
remove_secondary_response_model = family_info.model('RemoveSecondaryResponse',{
    "responseMessage": fields.String(example="Secondary User Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(relation_id_model)
})

add_member_model = family_info.model('AddMemberFields',{
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'vRelation':fields.String(example="Son"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1),
    'iRelationID' : fields.List(fields.String(description='To assign primary/secondary'))
})

add_member_response_model = family_info.model('AddMemberResponse',{
    "responseMessage": fields.String(example="Family Member Added"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(add_member_model)
})

user_model = family_info.model('UserFields', {
    'PK': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),    
    'vFullName':fields.String(example="John Doe"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
}) 


family_member_model = family_info.model('FamilyMemberFields', {
    'iFamMemID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),        
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
    'iFamMemID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=='),            
    'vFirstName':fields.String(example="test"),
    'vLastName':fields.String(example="test"),
    'vRelation':fields.String(example="Son"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1)
}) 
edit_member_response_model = family_info.model('EditMemberResponse',{
    "responseMessage": fields.String(example="Family Member Updated"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(edit_member_model)
})

remove_member_model = family_info.model('RemoveMemberFields', {
    'iFamMemID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=='),            
})
remove_member_response_model = family_info.model('RemoveMemberResponse',{
    "responseMessage": fields.String(example="Family Member Removed"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(remove_member_model)
})

assign_primary_secondary_model = family_info.model('AssignPrimarySecondaryFields',{
    'iFamMemID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=='),            
    'iRelationID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw==')  
})
assign_primary_response_model = family_info.model('AssignPrimaryResponse',{
    "responseMessage": fields.String(example="User Assigned"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(assign_primary_secondary_model)
})

assign_list_primary_secondary = family_info.model('AssignedListFields',{
    'iMemRelationID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=='),
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vFullName':fields.String(example="test test"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=1)
})
assign_primary_list_response = family_info.model('AssignedPrimaryListResponse',{
    "responseMessage": fields.String(example="Assigned Primary Users List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(assign_list_primary_secondary))
})
assign_secondary_list_response = family_info.model('AssignedSecondaryListResponse',{
    "responseMessage": fields.String(example="Assigned Secondary Users List"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(assign_list_primary_secondary))
})
unassign_model = family_info.model('UnassignFields',{
    'iMemRelationID': fields.String(example='gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=='),
})
unassign_response = family_info.model('UnassignResponse',{
    "responseMessage": fields.String(example="User Unassigned"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(unassign_model)
})
image_model = family_info.model('ImageURLFields',{
    'vImageURL': fields.String(example="")
})
video_model = family_info.model('VideoURLFields',{
    'vVideoURL': fields.String(example="")
})
tooth_event_model = family_info.model('ToothEventFields',{
    'iFamMemID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),
    'iToothCategoryID':  fields.Integer(example=2), 
    'vRightLeft':fields.String(example="L"),
    'vUpDown':fields.String(example="U"),
    'tiInput': fields.Integer(example=2),
    'tiEvent': fields.Integer(example=3),
    'eType': fields.String(example='adult'),
    'tComments' : fields.String(example="Test Comments"),
    'vImageURL' : fields.List(fields.String()),
    'vVideoURL' : fields.List(fields.String())
})

tooth_event_response = family_info.model('ToothEventResponse',{
    "responseMessage": fields.String(example="Tooth Event Created"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.Nested(tooth_event_model)
})

view_tooth_history_model = family_info.model('ViewToothHistoryFields',{
    'iFamMemID': fields.String(example="gAAAAABeCvRH4zXZa1efxNg5b-PMtdlhjsuQb7SPg_qbPybAm7pYNLHbt0HH1zB2q_e0SZiLGIeAjAvcb_58_7R3qTKOkrYfHw=="),
    'AddedBy' : fields.String(example="test test"),    
    'iToothCategoryID':  fields.Integer(example=2),
    'vFullName' : fields.String(example="John Doe"), 
    'tiInput': fields.Integer(example=2),
    'tiEvent': fields.Integer(example=3),
    'tComments' : fields.String(example="Test Comments"),
    'vImageURL' : fields.List(fields.String()),
    'vVideoURL' : fields.List(fields.String()),
    'tsCreatedAt' : fields.String()
})
view_tooth_history_response = family_info.model('ViewToothHistoryResponse',{
    "responseMessage": fields.String(example="Individual Tooth History"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(event_item_model))
})
view_all_history_response = family_info.model('ViewAllHistoryResponse',{
    "responseMessage": fields.String(example="All Tooth History"),
    "responseCode": fields.Integer(example=200),
    "responseData": fields.List(fields.Nested(view_tooth_history_model))
})

@family_info.route("/AddPrimary")
class AddPrimary(Resource):
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @family_info.response(200,"User Added",add_primary_response_model)
    @family_info.response(400,"Cannot Add More Users",error_response)
    @jwt_required    
    def post(self):
        """
        Add Primary User
        """
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.add_primary_secondary(data,iUserID,tiRelationType=1)

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
        return familyinfo.primary_secondary_list(iUserID,tiRelationType=1)

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
        return familyinfo.primary_secondary_list(iUserID,tiRelationType=2)


@family_info.route("/AddSecondary")
class AddSecondary(Resource):
    @family_info.response(200,"User Added",add_secondary_response_model)
    @family_info.response(400,"Cannot Add More Users",error_response)
    @family_info.doc(parser=jwt_parser,body=add_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Add Secondary User
        """
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.add_primary_secondary(data,iUserID,tiRelationType=2)


@family_info.route("/EditPrimary")
class EditPrimary(Resource):
    @family_info.marshal_with(edit_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=edit_primary_secondary_fields)
    @jwt_required    
    def put(self):
        """
        Edit Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.edit_primary_secondary(data,iUserID,tiRelationType=1)



@family_info.route("/EditSecondary")
class EditSecondary(Resource):
    @family_info.marshal_with(edit_secondary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=edit_primary_secondary_fields)
    @jwt_required    
    def put(self):
        """
        Edit Secondary User
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.edit_primary_secondary(data,iUserID,vDeviceUniqueID,tiRelationType=2)


@family_info.route("/RemovePrimary")
class RemovePrimary(Resource):
    @family_info.marshal_with(remove_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=relation_id_model)
    @jwt_required    
    def delete(self):
        """
        Remove Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.remove_primary_secondary(data,iUserID,tiRelationType=1)


@family_info.route("/RemoveSecondary")
class RemoveSecondary(Resource):
    @family_info.marshal_with(remove_secondary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=relation_id_model)
    @jwt_required    
    def delete(self):
        """
        Remove Secondary User
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.remove_primary_secondary(data,iUserID,tiRelationType=2)

@family_info.route("/AddFamilyMember")
class AddFamilyMember(Resource):
    @family_info.response(200,"Member Added",add_member_response_model)
    @family_info.response(400,"Cannot Add More Members",error_response)
    @family_info.doc(parser=jwt_parser,body=add_member_model)
    @jwt_required    
    def post(self):
        """
        Add Family Member
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        data = request.json
        return familyinfo.add_family_member(data,iUserID,vDeviceUniqueID)


@family_info.route("/GetFamilyInformation")
class GetFamilyInformation(Resource):
    @family_info.marshal_with(get_family_info_response_model, code=200)
    @family_info.doc(parser=jwt_parser)
    @jwt_required    
    def get(self):
        """
        Get Family Information 
        """
        iUserID = get_jwt_identity()
        return familyinfo.get_family_info(iUserID)


@family_info.route("/GetToothPalette")
class GetToothPalette(Resource):
    # @family_info.marshal_with(get_tooth_palette_response, code=200)
    @family_info.doc(parser=jwt_parser)
    @jwt_required    
    def get(self):
        """
        Get Tooth Palette  
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        return familyinfo.get_tooth_palette(iUserID,vDeviceUniqueID)


@family_info.route("/EditFamilyMember")
class EditFamilyMember(Resource):
    @family_info.marshal_with(edit_member_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=edit_member_model)
    @jwt_required    
    def put(self):
        """
        Edit Family Member
        """
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.edit_family_member(data,iUserID)


@family_info.route("/RemoveFamilyMember")
class RemoveFamilyMember(Resource):
    @family_info.marshal_with(remove_member_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=remove_member_model)
    @jwt_required    
    def delete(self):
        """
        Remove Family Member
        """
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.remove_family_member(data,iUserID)

@family_info.route("/AssignPrimary")
class AssignPrimary(Resource):
    @family_info.marshal_with(assign_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=assign_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Assign Primary User
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.assign_primary_secondary(data,iUserID,tiRelationType=1,add_assign=0)

@family_info.route("/AssignSecondary")
class AssignSecondary(Resource):
    @family_info.marshal_with(assign_primary_response_model, code=200)
    @family_info.doc(parser=jwt_parser,body=assign_primary_secondary_model)
    @jwt_required    
    def post(self):
        """
        Assign Secondary User
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.assign_primary_secondary(data,iUserID,tiRelationType=2,add_assign=0)

@family_info.route("/ViewPrimaryAssigned")
class ViewPrimaryAssigned(Resource):
    @family_info.marshal_with(assign_primary_list_response, code=200)
    @family_info.doc(parser=jwt_parser,body=remove_member_model)
    @jwt_required    
    def post(self):
        """
        View Primary Assigned 
        """
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.assign_list(data,iUserID,tiRelationType=1)

@family_info.route("/ViewSecondaryAssigned")
class ViewSecondaryAssigned(Resource):
    @family_info.marshal_with(assign_secondary_list_response, code=200)
    @family_info.doc(parser=jwt_parser,body=remove_member_model)
    @jwt_required    
    def post(self):
        """
        View Secondary Assigned 
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.assign_list(data,iUserID,tiRelationType=2)

@family_info.route("/Unassign")
class UnassignPrimary(Resource):
    @family_info.marshal_with(unassign_response, code=200)
    @family_info.doc(parser=jwt_parser,body=unassign_model)
    @jwt_required    
    def delete(self):
        """
        Unassign Primary/Secondary
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.unassign(data,iUserID)



@family_info.route("/AddToothEvent")
class AddToothEvent(Resource):
    @family_info.marshal_with(tooth_event_response, code=200)
    @family_info.doc(parser=jwt_parser,body=tooth_event_model)
    @jwt_required    
    def post(self):
        """
        Add Tooth Event 
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.add_tooth_input(data,iUserID)


@family_info.route("/ViewIndividualToothHistory")
class ViewToothHistory(Resource):
    @family_info.marshal_with(view_tooth_history_response, code=200)
    @family_info.doc(parser=jwt_parser,body=remove_member_model)
    @jwt_required    
    def post(self):
        """
        View Individual Tooth History
        """
        # try:
        iUserID = get_jwt_identity()
        data = request.json
        return familyinfo.view_tooth_history(data,iUserID,get_list = 0,tooth_gallery=0)

@family_info.route("/ViewAllToothHistory")
class ViewToothHistory(Resource):
    @family_info.marshal_with(view_all_history_response, code=200)
    @family_info.doc(parser=jwt_parser)
    @jwt_required
    def get(self):
        """
        View All Tooth History
        """
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
        events_list =  home.get_events_list(iUserID,vDeviceUniqueID)
        return response.send_response(200,"All Tooth History",events_list)