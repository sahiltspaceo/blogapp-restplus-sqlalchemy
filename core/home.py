from database.models import (UserModel, UserRelationshipModel,
							FamilyMemberRelationshipModel,AppointmentModel,
							DentistModel)
from .utils import (get_lang_json,find_by_userid,get_fullname_by_member_id,encrypt,get_offset_by_id,
                    get_own_family_members,get_relations_from_touserid,get_assigned_members_from_relationID,
                    divide_list_chunks)
from .familyinfo import view_tooth_history
from . import response

import datetime as dt

def home_screen(data,iUserID, vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    ### User Dict
    user_db_obj = UserModel.query.filter_by(iUserID=iUserID).with_entities(UserModel.vFullName,UserModel.vProfilePicURL).first()    
    user_dict = {
        'vFullName' : user_db_obj[0],
        'vProfilePicURL' : user_db_obj[1]
    }

    ### Appointments List
    client_local_datetime = dt.datetime.utcnow() + dt.timedelta(minutes=get_offset_by_id(iUserID))
    client_local_date = client_local_datetime.date()

    appointment_list = []
    appoint_db_obj = AppointmentModel.query.filter_by(iUserID=iUserID,iFamMemID = None,dDateOfAppoint=client_local_date).with_entities(AppointmentModel.iFamMemID,AppointmentModel.iDentistID,AppointmentModel.tTimeOfAppoint).all()
    for appoint_db in appoint_db_obj:
        member_obj = UserModel.query.filter_by(iUserID=iUserID).with_entities(UserModel.vFullName,UserModel.vProfilePicURL).first()
        vFullName = member_obj[0]
        vProfilePicURL = member_obj[1]

        appoint_dict = {
            'vFullName' : vFullName,
            'vProfilePicURL': vProfilePicURL,
            'vDentistName': DentistModel.query.filter_by(iDentistID=appoint_db[1]).with_entities(DentistModel.vDentistName).first()[0],
            'tTimeOfAppoint': appoint_db[2],
        }
        appointment_list.append(appoint_dict)

    
    own_fam_members = get_own_family_members(iUserID)
    for members in own_fam_members:
        appoint_db_obj = AppointmentModel.query.filter_by(iFamMemID = members[0],dDateOfAppoint = client_local_date).with_entities(AppointmentModel.iFamMemID,AppointmentModel.iDentistID,AppointmentModel.tTimeOfAppoint).all()
        for appoint_db in appoint_db_obj:
            vFullName = get_fullname_by_member_id(iFamMemID=appoint_db[0])
            vProfilePicURL = None

            appoint_dict = {
                'vFullName' : vFullName,
                'vProfilePicURL': vProfilePicURL,
                'vDentistName': DentistModel.query.filter_by(iDentistID=appoint_db[1]).with_entities(DentistModel.vDentistName).first()[0],
                'tTimeOfAppoint': appoint_db[2],
            }
            appointment_list.append(appoint_dict)

    
    relation_obj =  UserRelationshipModel.query.filter_by(iToUserID = iUserID,tiRelationType=1).with_entities(UserRelationshipModel.iRelationID).all()
    for relation in relation_obj:
        iFamMemID = FamilyMemberRelationshipModel.query.filter_by(iRelationID = relation[0]).with_entities(FamilyMemberRelationshipModel.iFamMemID).first()
        if iFamMemID is not None:
            appoint_db_obj = AppointmentModel.query.filter_by(iFamMemID = iFamMemID[0],dDateOfAppoint=client_local_date).with_entities(AppointmentModel.iDentistID,AppointmentModel.tTimeOfAppoint).first()
            if appoint_db_obj is not None:
                appoint_dict = {
                    'vFullName' : get_fullname_by_member_id(iFamMemID=iFamMemID[0]),
                    'vProfilePicURL': None,
                    'vDentistName': DentistModel.query.filter_by(iDentistID=appoint_db_obj[0]).with_entities(DentistModel.vDentistName).first()[0],
                    'tTimeOfAppoint': appoint_db_obj[1]
                }
                appointment_list.append(appoint_dict)

    appointment_list.sort(key = lambda x:x['tTimeOfAppoint']) 
    
    page_appointment_list = list(divide_list_chunks(divide_list=appointment_list,ItemsPerPage = data['AppointmentsPagination']['ItemsPerPage']))
    page_appointment_list = page_appointment_list[data['AppointmentsPagination']['PageIndex']] if len(page_appointment_list) != 0 else None

    appointment_response = {
        'TotalItems' : len(appointment_list),
        'AppointmentItems' : page_appointment_list
    }


    events_list = get_events_list(iUserID,vDeviceUniqueID)
    events_list.sort(key=lambda x: x['tsCreatedAt'])
    events_list.reverse()

    page_events_list = list(
        divide_list_chunks(divide_list=events_list, ItemsPerPage=data['EventsPagination']['ItemsPerPage']))
    page_events_list = page_events_list[data['EventsPagination']['PageIndex']] if len(page_events_list) != 0 else None

    events_response = {
        'TotalItems' : len(events_list),
        'HomeEventItems' : page_events_list
    }

    response_dict = {
        'User': user_dict,
        'Appointments' : appointment_response,
        'Events' : events_response,
    }
    

    return response.send_response(200, lang_response['home']['home_screen'], response_dict)

def get_events_list(iUserID,vDeviceUniqueID):
    ### Events List
    events_list = []
    tooth_list = []

    own_fam_members = get_own_family_members(iUserID)
    for members in own_fam_members:
        ### User's Own Family Members Tooth History
        tooth_history_list = view_tooth_history(data={"iFamMemID": encrypt(str(members[0]))}, iUserID=iUserID,
                                                get_list=1, tooth_gallery=0)
        for item in tooth_history_list:
            tooth_list.append(item['iToothHisID'])
        events_list.extend(tooth_history_list)

    assigned_members_obj = get_relations_from_touserid(iUserID)
    for assigned_members in assigned_members_obj:
        assigned_fam_mem = get_assigned_members_from_relationID(assigned_members[0])
        for members in assigned_fam_mem:
            ### User's Assigned Family Members Tooth History
            tooth_history_list = view_tooth_history(data={"iFamMemID": encrypt(str(members[0]))}, iUserID=iUserID,
                                                    get_list=1, tooth_gallery=0)
            for item in tooth_history_list:
                if item['iToothHisID'] not in tooth_list:
                    events_list.append(item)
                    tooth_list.append(item['iToothHisID'])

    ### User's Own Tooth History
    tooth_history_list = view_tooth_history(data={"iFamMemID": ""}, iUserID=iUserID,
                                            get_list=1, tooth_gallery=0)
    events_list.extend(tooth_history_list)
    return  events_list
