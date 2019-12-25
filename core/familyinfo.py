from database import db
from database.models import (UserModel, UserRelationshipModel, DeviceModel,
                            FamilyMemberModel,FamilyMemberRelationshipModel)
from . import response
from .users import find_by_email, find_id_by_email, find_by_userid
from .utils import (get_lang_json, is_authorized, check_if_relationship_exists,check_family_member_limit,
                    find_email_by_id, check_relationship_limit,get_user_relation_object,get_user_dict,
                    get_primary_list,get_family_members_list,get_secondary_for_list)


def add_primary_secondary(data, iUserID, vDeviceUniqueID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    if not check_relationship_limit(iFromUserID=iUserID, tiRelationType=tiRelationType):
        return response.send_response(400, lang_response['familyinfo']['max_limit_reached'], None)

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
            return response.send_response(400, lang_response['familyinfo']['user_already_added'], data)

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


def edit_primary_secondary(data,iUserID, vDeviceUniqueID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    user_relation_obj = get_user_relation_object(iFromUserID = iUserID, iToUserID = find_id_by_email(data['vEmail']), tiRelationType=tiRelationType)
    user_relation_obj.vFirstName = data['vFirstName']
    user_relation_obj.vLastName = data['vLastName']
    user_relation_obj.dDOB = data['dDOB']
    user_relation_obj.tiGender = data['tiGender']
    db.session.commit()

    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_user_updated'], data)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_user_updated'], data)


def primary_secondary_list(iUserID, vDeviceUniqueID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    response_list = []

    db_obj = UserRelationshipModel.query.filter_by(iFromUserID=iUserID).filter_by(tiRelationType=tiRelationType).with_entities(
            UserRelationshipModel.vFirstName, UserRelationshipModel.vLastName, UserRelationshipModel.iToUserID,UserRelationshipModel.dDOB,UserRelationshipModel.tiGender,UserRelationshipModel.iRelationID).all()
    for obj in db_obj:
        obj_dict = {
                'iRelationID': obj[5],
                'vFirstName': obj[0],
                'vLastName': obj[1],
                'vEmail': find_email_by_id(obj[2]),
                'dDOB' : obj[3],
                'tiGender' : obj[4]
        }
        response_list.append(obj_dict)
    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_list'], response_list)
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_list'], response_list)

def remove_primary_secondary(data,iUserID, vDeviceUniqueID, tiRelationType):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    UserRelationshipModel.query.filter_by(iToUserID=find_id_by_email(data['vEmail']),iFromUserID = iUserID,tiRelationType=tiRelationType).delete()
    db.session.commit()

    if tiRelationType == 1:
        return response.send_response(200, lang_response['familyinfo']['primary_removed'], {"vEmail":data['vEmail']})
    else:
        return response.send_response(200, lang_response['familyinfo']['secondary_removed'], {"vEmail":data['vEmail']})    

def add_family_member(data,iUserID, vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    if not check_family_member_limit(iUserID):
        return response.send_response(400, lang_response['familyinfo']['family_member_limit_reached'], None)
    
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

    return response.send_response(200, lang_response['familyinfo']['family_member_added'], data)

def get_family_info(iUserID,vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

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


def edit_family_member(data,iUserID,vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    db_obj = FamilyMemberModel.query.filter_by(iFamMemID=data['iFamMemID']).first()
    db_obj.vFirstName = data['vFirstName']
    db_obj.vLastName = data['vLastName']
    db_obj.tiGender = data['tiGender']
    db_obj.vRelation = data['vRelation']
    db_obj.dDOB = data['dDOB']
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['family_member_updated'], data)

def remove_family_member(data,iUserID,vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID, vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    FamilyMemberModel.query.filter_by(iFamMemID=data['iFamMemID']).delete()
    db.session.commit()

    return response.send_response(200, lang_response['familyinfo']['family_member_removed'], data)

 