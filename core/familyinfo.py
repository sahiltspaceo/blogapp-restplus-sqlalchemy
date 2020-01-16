from database import db
from database.models import (UserModel, UserRelationshipModel,
                            FamilyMemberModel,FamilyMemberRelationshipModel,ToothEventModel,
                            ToothMediaModel,ToothStructureModel)
from . import response
from .users import find_by_email, find_id_by_email, find_by_userid
from .utils import (get_lang_json, check_if_relationship_exists,check_family_member_limit,
                    find_email_by_id, check_relationship_limit,get_user_relation_object,get_user_dict,
                    get_primary_list,get_family_members_list,get_secondary_for_list,check_assign_limit,
                    encrypt,decrypt,get_fullname_by_member_id,get_local_datetime)
import datetime


def add_primary_secondary(data, iUserID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if data['vEmail'] == find_email_by_id(iUserID):
        return response.send_error_response(400, lang_response['familyinfo']['cannot_add_self_email'])

    if not check_relationship_limit(iFromUserID=iUserID, tiRelationType=tiRelationType):
        return response.send_error_response(400, lang_response['familyinfo']['max_limit_reached'])

    if find_by_email(data['vEmail']) is None:
        new_user = UserModel(
                vEmail=data['vEmail'],
                tiIsRegistered=0
        )
        db.session.add(new_user)
        db.session.commit()
        db.session.flush()
        iToUserID = new_user.iUserID

    else:
        iToUserID = find_id_by_email(data['vEmail'])
        if check_if_relationship_exists(iFromUserID=iUserID, iToUserID=iToUserID, tiRelationType=tiRelationType):
            return response.send_error_response(400, lang_response['familyinfo']['user_already_added'])

    user_relation = UserRelationshipModel(
        iFromUserID=iUserID,
        iToUserID=iToUserID,
        tiRelationType=tiRelationType,
        vFirstName=data['vFirstName'],
        vLastName=data['vLastName'],
        dDOB=data['dDOB'],
        tiGender=data['tiGender'],
    )

    db.session.add(user_relation)
    db.session.commit()
    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_user_added'], data)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_user_added'], data)


def edit_primary_secondary(data,iUserID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)


    user_relation_obj = get_user_relation_object(iRelationID = decrypt(data['iRelationID']))
    user_relation_obj.vFirstName = data['vFirstName']
    user_relation_obj.vLastName = data['vLastName']
    user_relation_obj.dDOB = data['dDOB']
    user_relation_obj.tiGender = data['tiGender']
    user_relation_obj.tsUpdatedAt = datetime.datetime.now()    
    db.session.commit()

    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_user_updated'], data)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_user_updated'], data)


def primary_secondary_list(iUserID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []

    db_obj = UserRelationshipModel.query.filter_by(iFromUserID=iUserID).filter_by(tiRelationType=tiRelationType).with_entities(
            UserRelationshipModel.vFirstName, UserRelationshipModel.vLastName, UserRelationshipModel.iToUserID,UserRelationshipModel.dDOB,UserRelationshipModel.tiGender,UserRelationshipModel.iRelationID).all()
    for obj in db_obj:
        obj_dict = {
                'iRelationID': encrypt(str(obj[5])),
                'vFullName': obj[0] + " " + obj[1],
                'vEmail': find_email_by_id(obj[2]),
                'dDOB' : obj[3],
                'tiGender' : obj[4]
        }
        response_list.append(obj_dict)
    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_list'], response_list)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_list'], response_list)

def remove_primary_secondary(data,iUserID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    UserRelationshipModel.query.filter_by(iRelationID=decrypt(data['iRelationID'])).delete()
    db.session.commit()

    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_removed'], data)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_removed'], data)    

def add_family_member(data,iUserID, vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not check_family_member_limit(iUserID):
        return response.send_error_response(400, lang_response['familyinfo']['family_member_limit_reached'])
    
    family_member = FamilyMemberModel(
        iUserID = iUserID,
        vFirstName=data['vFirstName'],
        vLastName=data['vLastName'],
        dDOB=data['dDOB'],
        tiGender=data['tiGender'],
        vRelation = data['vRelation']
    )
    db.session.add(family_member)
    db.session.commit()
    db.session.flush()

    if len(data['iRelationID']) != 0:
        for ID in data['iRelationID']:
            assign = {
                'iFamMemID' : encrypt(str(family_member.iFamMemID)),
                'iRelationID' : ID
            }
            tiRelationType = UserRelationshipModel.query.filter_by(iRelationID=decrypt(ID)).with_entities(UserRelationshipModel.tiRelationType).first()[0]
            if assign_primary_secondary(data=assign,iUserID=iUserID,tiRelationType=tiRelationType,add_assign=1):
                pass
            else:
                db.session.rollback()
                return response.send_error_response(400, lang_response['familyinfo']['assign_max_reached'])

    return response.send_response(200, lang_response['familyinfo']['family_member_added'], data)

def get_family_info(iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    user_dict = get_user_dict(iUserID)
    primary_list = get_primary_list(iUserID)
    family_members_list = get_family_members_list(iUserID)
    secondary_for_list = get_secondary_for_list(iUserID)    

    get_family_info_response = {
        "User" : user_dict,
        "PrimaryMembers":primary_list,
        "FamilyMembers":family_members_list,
        "SecondaryFor": secondary_for_list
    }
    return response.send_response(200, lang_response['familyinfo']['family_info'], get_family_info_response)


def edit_family_member(data,iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    db_obj = FamilyMemberModel.query.filter_by(iFamMemID=decrypt(data['iFamMemID'])).first()
    db_obj.vFirstName = data['vFirstName']
    db_obj.vLastName = data['vLastName']
    db_obj.tiGender = data['tiGender']
    db_obj.vRelation = data['vRelation']
    db_obj.dDOB = data['dDOB']
    db_obj.tsUpdatedAt = datetime.datetime.now()
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['family_member_updated'], data)

def remove_family_member(data,iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    FamilyMemberModel.query.filter_by(iFamMemID=decrypt(data['iFamMemID'])).delete()
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['family_member_removed'], data)

def assign_primary_secondary(data,iUserID,tiRelationType,add_assign):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not check_assign_limit(iFamMemID = decrypt(data['iFamMemID']),tiRelationType=tiRelationType):
        if add_assign == 1:
            return False
        else:
            return response.send_response(400, lang_response['familyinfo']['assign_max_reached'], data)

    assign_primary_secondary_obj = FamilyMemberRelationshipModel(
        iFamMemID = decrypt(data['iFamMemID']),
        iRelationID = decrypt(data['iRelationID'])
    )
    db.session.add(assign_primary_secondary_obj)
    db.session.commit()

    if add_assign == 1:
        return True
    else:
        return response.send_response(200, lang_response['familyinfo']['user_assigned'], data)


def assign_list(data,iUserID,tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    assigned_list = []
    
    db_obj = FamilyMemberRelationshipModel.query.filter_by(iFamMemID=decrypt(data['iFamMemID'])).with_entities(FamilyMemberRelationshipModel.iMemRelationID,FamilyMemberRelationshipModel.iRelationID).all()
    for obj in db_obj:
        list_obj = UserRelationshipModel.query.filter_by(iRelationID=obj[1]).with_entities(
                    UserRelationshipModel.vFirstName, UserRelationshipModel.vLastName,UserRelationshipModel.iToUserID,UserRelationshipModel.dDOB,UserRelationshipModel.tiGender,UserRelationshipModel.tiRelationType).first()
        if list_obj[5] == tiRelationType:
            assign_obj = {
                "iMemRelationID" : encrypt(str(obj[0])),
                "vFullName" : list_obj[0] +" "+ list_obj[1],
                "dDOB" : list_obj[3],
                "tiGender" : list_obj[4],
                "vEmail" : find_email_by_id(list_obj[2])
            }
            assigned_list.append(assign_obj)
    
    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['assigned_primary_list'], assigned_list)
    else:
        return response.send_response(200, lang_response['familyinfo']['assigned_secondary_list'], assigned_list)

def unassign(data,iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    FamilyMemberRelationshipModel.query.filter_by(iMemRelationID=decrypt(data['iMemRelationID'])).delete()
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['unassigned'], data)

def add_tooth_input(data,iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    iToothID = ToothStructureModel.query.filter_by(iToothCategoryID=data['iToothCategoryID'],vRightLeft=data['vRightLeft'],vUpDown=data['vUpDown'],eType=data['eType']).with_entities(ToothStructureModel.iToothID).first()[0]
    
    iFamMemID = decrypt(data['iFamMemID']) if data['iFamMemID'] != "" else None
    iFamMemID = int(iFamMemID or 0)


    new_event = ToothEventModel(
        iUserID = iUserID,
        iFamMemID = None if iFamMemID == 0 else iFamMemID,
        iToothID = iToothID,
        tiInput = data['tiInput'],
        tiEvent = data['tiEvent'],
        tComments = data['tComments']
    )
    db.session.add(new_event)
    db.session.commit()
    db.session.flush()

    for image in data['vImageURL']:
        new_media = ToothMediaModel(
            iToothHisID = new_event.iToothHisID,
            vMediaURL = image,
            tiMediaType = 1
        )
        db.session.add(new_media)

    for video in data['vVideoURL']:
        new_media = ToothMediaModel(
            iToothHisID = new_event.iToothHisID,
            vMediaURL = video,
            tiMediaType = 2
        )
        db.session.add(new_media)
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['tooth_event_created'], data)

def view_tooth_history(data,iUserID,get_list,tooth_gallery):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []
    tooth_gallery_list = []

    if data['iFamMemID'] == "":
        db_obj = ToothEventModel.query.with_entities(ToothEventModel.iToothHisID,ToothEventModel.iUserID,ToothEventModel.iToothID,ToothEventModel.tiInput,ToothEventModel.tiEvent,ToothEventModel.tComments,ToothEventModel.tsCreatedAt).filter_by(iUserID=iUserID,iFamMemID=None).all()
        vFullName = UserModel.query.with_entities(UserModel.vFullName).filter_by(iUserID=iUserID).first()[0]
    else:
        db_obj = ToothEventModel.query.with_entities(ToothEventModel.iToothHisID,ToothEventModel.iUserID,ToothEventModel.iToothID,ToothEventModel.tiInput,ToothEventModel.tiEvent,ToothEventModel.tComments,ToothEventModel.tsCreatedAt).filter_by(iFamMemID=decrypt(data['iFamMemID'])).all()
        vFullName = get_fullname_by_member_id(iFamMemID=decrypt(data['iFamMemID']))

    for obj in db_obj: 
        image_urls = []
        video_urls = []
        media_obj = ToothMediaModel.query.with_entities(ToothMediaModel.vMediaURL,ToothMediaModel.tiMediaType).filter_by(iToothHisID=obj[0]).all()
        for media in media_obj:
            if media[1] == 1:
                if tooth_gallery == 1:
                    tooth_gallery_response = {
                        'iToothHisID' : obj[0],
                        'iFamMemID' : encrypt(str(data['iFamMemID'])) if data['iFamMemID'] != "" else None,
                        'vMediaURL' : media[0],
                        'vFullName' : vFullName,
                        'tsCreatedAt' : get_local_datetime(datestring=obj[6],iUserID=iUserID),
                        'vMediaType' : 'Image'
                    }
                    tooth_gallery_list.append(tooth_gallery_response)
                else:
                    image_urls.append(media[0])
            else:
                if tooth_gallery == 1:
                    tooth_gallery_response = {
                        'iToothHisID' : obj[0],
                        'iFamMemID' : encrypt(str(data['iFamMemID'])) if data['iFamMemID'] != "" else None,
                        'vFullName' : vFullName,
                        'vMediaURL' : media[0],
                        'tsCreatedAt' : get_local_datetime(datestring=obj[6],iUserID=iUserID),
                        'vMediaType' : 'Video'
                    }
                    tooth_gallery_list.append(tooth_gallery_response)
                else:
                    video_urls.append(media[0])

        response_json = {
            'iToothHisID' : obj[0],
            'AddedBy' : UserModel.query.filter_by(iUserID=obj[1]).with_entities(UserModel.vFullName).first()[0] if (obj[1] != iUserID) else None,
            'iFamMemID' : data['iFamMemID'],
            'iToothCategoryID' : ToothStructureModel.query.filter_by(iToothID = obj[2]).with_entities(ToothStructureModel.iToothCategoryID).first()[0],
            'vFullName' : vFullName,
            'tiInput' : obj[3],
            'tiEvent' : obj[4],
            'tComments' : obj[5],
            'tsCreatedAt' : get_local_datetime(datestring=obj[6],iUserID=iUserID),
            'vImageURL' : image_urls,
            'vVideoURL' : video_urls
        }

        response_list.append(response_json)
    if get_list == 0 and tooth_gallery == 0:
        return response.send_response(200, lang_response['familyinfo']['tooth_history'], response_list)
    elif get_list == 1 and tooth_gallery ==0: 
        return response_list
    elif get_list == 0 and tooth_gallery == 1:
        return tooth_gallery_list


def get_tooth_palette(iUserID,vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []

    if data['iFamMemID'] == "":
        db_obj = ToothEventModel.query.with_entities(ToothEventModel.iToothHisID,ToothEventModel.iUserID,ToothEventModel.iToothID,ToothEventModel.tiInput,ToothEventModel.tiEvent,ToothEventModel.tComments,ToothEventModel.tsCreatedAt).filter_by(iUserID=iUserID,iFamMemID=None).all()
        vFullName = UserModel.query.with_entities(UserModel.vFullName).filter_by(iUserID=iUserID).first()[0]
    else:
        db_obj = ToothEventModel.query.with_entities(ToothEventModel.iToothHisID,ToothEventModel.iUserID,ToothEventModel.iToothID,ToothEventModel.tiInput,ToothEventModel.tiEvent,ToothEventModel.tComments,ToothEventModel.tsCreatedAt).filter_by(iFamMemID=decrypt(data['iFamMemID'])).all()
        vFullName = get_fullname_by_member_id(iFamMemID=decrypt(data['iFamMemID']))
