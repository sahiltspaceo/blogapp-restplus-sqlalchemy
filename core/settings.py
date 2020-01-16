from database import db
from database.models import (ToothDiseaseModel, UserModel,RevokedTokenModel,DeviceModel,CMSPagesModel)
from .utils import (get_lang_json,get_own_family_members, encrypt, get_relations_from_touserid,
    get_assigned_members_from_relationID, find_by_userid, find_by_email, generate_hash)
from .familyinfo import view_tooth_history
from . import response

import datetime


def tooth_disease(iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []
    toothdisease = ToothDiseaseModel.query.all()
    for disease in toothdisease:
        tooth_disease_dict = {
            'vTitle': disease.vTitle,
            'tContent': disease.tContent
        }
        response_list.append(tooth_disease_dict)

    return response.send_response(200, lang_response['settings']['tooth_diseases'], response_list)


def tooth_gallery(iUserID, vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []
    tooth_list = []

    own_fam_members = get_own_family_members(iUserID)
    for members in own_fam_members:

        # User's Own Family Members Tooth Gallery
        tooth_gallery_list = view_tooth_history(data={"iFamMemID": encrypt(str(
            members[0]))}, iUserID=iUserID, get_list=0, tooth_gallery=1)
        response_list.extend(tooth_gallery_list)

    assigned_members_obj = get_relations_from_touserid(iUserID)
    for assigned_members in assigned_members_obj:
        assigned_fam_mem = get_assigned_members_from_relationID(
            assigned_members[0])
        for members in assigned_fam_mem:

            # User's Assigned Family Members Tooth History
            tooth_gallery_list = view_tooth_history(data={"iFamMemID": encrypt(str(
                members[0]))}, iUserID=iUserID, get_list=0, tooth_gallery=1)
            for item in tooth_gallery_list:
                if item['iToothHisID'] not in tooth_list:
                    response_list.append(item)
                    tooth_list.append(item['iToothHisID'])

    # User's Own Tooth Gallery
    tooth_gallery_list = view_tooth_history(
        data={"iFamMemID": ""}, iUserID=iUserID, get_list=0, tooth_gallery=1)
    response_list.extend(tooth_gallery_list)

    return response.send_response(200, lang_response['settings']['tooth_gallery'], response_list)


def view_profile(iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    profile_obj = UserModel.query.filter_by(iUserID=iUserID).with_entities(UserModel.vFullName, UserModel.vMobile,
                                                                           UserModel.tiGender, UserModel.vCountryCode, UserModel.vEmail, UserModel.dDOB, UserModel.vProfilePicURL).first()
    response_dict = {
        'vEmail': profile_obj[4],
        'vFullName': profile_obj[0],
        'vCountryCode': profile_obj[3],
        'vMobile': profile_obj[1],
        'dDOB': profile_obj[5],
        'vProfilePicURL': profile_obj[6]
    }

    return response.send_response(200, lang_response['settings']['view_profile'], response_dict)


def update_profile(data, iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    profile_obj = find_by_userid(iUserID)
    profile_obj.vEmail = data['vEmail']
    profile_obj.vFullName = data['vFullName']
    profile_obj.vCountryCode = data['vCountryCode']
    profile_obj.vMobile = data['vMobile']
    profile_obj.dDOB = data['dDOB']
    profile_obj.vProfilePicURL = data['vProfilePicURL']
    profile_obj.tsUpdatedAt = datetime.datetime.now()

    db.session.add(profile_obj)
    db.session.commit()

    return response.send_response(200, lang_response['settings']['update_profile'], data)


def user_logout(AccessToken, iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    DeviceModel.query.filter_by(iUserID=iUserID).delete()

    revoke_token = RevokedTokenModel(
    	vToken=AccessToken
    )
    db.session.add(revoke_token)
    db.session.commit()

    return response.send_response(200, lang_response['onboarding']['logout_success'], None)


def update_password(data):
    current_user = find_by_email(data['vEmail'])
    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)

    current_user.vPassword = generate_hash(data['vPassword'])
    db.session.commit()

    return response.send_response(200, lang_response['settings']['password_updated'], {'vEmail': data['vEmail']})

def get_cms(iUserID,data):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    cms = CMSPagesModel.query.filter_by(vCMSTitle=data).with_entities(CMSPagesModel.tContent).first()[0]

    response_dict = {
        'CMS' : data,
        'Content' : cms
    }
    return response.send_response(200, lang_response['settings']['cms'],response_dict)
    