from database import db
from database.models import (UserModel, RevokedTokenModel, DeviceModel, UserRelationshipModel,
							FamilyMemberModel,FamilyMemberRelationshipModel)
from . import response
import app
import config
from app import UserObject
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from passlib.hash import pbkdf2_sha256 as sha256
import json
import os


def is_authorized(iUserID, vDeviceUniqueID):
    print(iUserID,vDeviceUniqueID)
    return DeviceModel.query.filter_by(iUserID=iUserID).filter_by(vDeviceUniqueID=vDeviceUniqueID).first()


def get_lang_json(lang):
    with open(os.path.join(app.BASE_DIR, 'language/%s.json' % lang)) as json_file:
        return json.load(json_file)


def find_by_email(email):
    return UserModel.query.filter_by(vEmail=email).first()


def find_by_userid(userid):
    return UserModel.query.filter_by(iUserID=userid).first()


def find_email_by_id(iUserID):
    return UserModel.query.with_entities(UserModel.vEmail).filter_by(iUserID=iUserID).first()[0]


def find_id_by_email(email):
    return UserModel.query.with_entities(UserModel.iUserID).filter_by(vEmail=email).first()[0]


def generate_hash(password):
    return sha256.hash(password)


def verify_hash(password, hash):
    return sha256.verify(password, hash)


def is_token_blacklisted(token):
    query = RevokedTokenModel.query.filter_by(vtoken=token).first()
    return bool(query)


def get_access_token(iUserID, vDeviceUniqueID):
    user = UserObject(iUserID=iUserID, vDeviceUniqueID=vDeviceUniqueID)
    return create_access_token(identity=user)


def check_if_relationship_exists(iFromUserID, iToUserID, tiRelationType):
    if UserRelationshipModel.query.filter_by(iFromUserID=iFromUserID).filter_by(iToUserID=iToUserID).filter_by(tiRelationType=tiRelationType).first() is not None:
        return True
    else:
        return False


def check_if_primary_count_exceeded(iToUserID):
    if UserRelationshipModel.query.filter_by(iToUserID=iToUserID).filter_by(tiRelationType=1).count() >= config.PRIMARY_USER_LIMIT:
        return True
    else:
        return False


def check_relationship_limit(iFromUserID, tiRelationType):
    if tiRelationType == 1:
        if UserRelationshipModel.query.filter_by(iFromUserID=iFromUserID).filter_by(tiRelationType=tiRelationType).count() < config.MAX_PRIMARY_LIMIT:
            return True
        else:
            return False
    else:
        if UserRelationshipModel.query.filter_by(iFromUserID=iFromUserID).filter_by(tiRelationType=tiRelationType).count() < config.MAX_SECONDARY_LIMIT:
            return True
        else:
            return False

def get_user_relation_object(iFromUserID,iToUserID,tiRelationType):
    return UserRelationshipModel.query.filter_by(iToUserID=iToUserID,iFromUserID = iFromUserID,tiRelationType=tiRelationType).first()

def check_family_member_limit(iUserID):
    own_count = FamilyMemberModel.query.filter_by(iUserID=iUserID).count()
    iRelationID = UserRelationshipModel.query.filter_by(iToUserID=iUserID,tiRelationType=1).with_entities(UserRelationshipModel.iRelationID)
    if iRelationID is not None:
        assigned_count = FamilyMemberRelationshipModel.query.filter_by(iRelationID = iRelationID).count()
    else:
        assigned_count = 0

    if own_count + assigned_count < config.MAX_FAMILY_MEMBER_LIMIT:
        return True
    else:
        return False

def get_user_dict(iUserID):
    db_obj = UserModel.query.with_entities(UserModel.dDOB,UserModel.vFullName,UserModel.iUserID).filter_by(iUserID=iUserID).first()
    user_dict = {
        "PK" : db_obj[2],
        "dDOB" : db_obj[0],
        "vFullName" : db_obj[1]
    }
    return user_dict

def get_primary_list(iUserID):
    primary_list = []
    db_obj =  UserRelationshipModel.query.filter_by(iFromUserID = iUserID,tiRelationType=1).with_entities(UserRelationshipModel.dDOB,UserRelationshipModel.vFirstName,UserRelationshipModel.vLastName,UserRelationshipModel.iRelationID).all()
    for obj in db_obj:
        primary_dict = {
            "PK" : obj[3],
            "vFullName" : obj[1] +" "+ obj[2],
            "dDOB" : obj[0]
        }
        primary_list.append(primary_dict)
    return primary_list

def get_family_members_list(iUserID):
    family_members_list = []
    db_obj = FamilyMemberModel.query.filter_by(iUserID=iUserID).with_entities(FamilyMemberModel.iFamMemID,FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName,FamilyMemberModel.dDOB,FamilyMemberModel.vRelation).all()

    for obj in db_obj:
        iFamMemID = obj[0]
        iRelationID = FamilyMemberRelationshipModel.query.filter_by(iFamMemID =iFamMemID).with_entities(FamilyMemberRelationshipModel.iRelationID)
        if iRelationID is not None:
            primary_count = UserRelationshipModel.query.filter_by(iRelationID = iRelationID,tiRelationType = 1).count()
            secondary_count = UserRelationshipModel.query.filter_by(iRelationID = iRelationID,tiRelationType = 2).count()
        else:
            primary_count = 0
            secondary_count = 0
       
        members_dict = {
        "iFamMemID" : iFamMemID,
        "AddedBy": None,
        "vRelation": obj[4],
        "vFullName": obj[1] +" "+ obj[2],
        "dDOB": obj[3],
        "SecondaryCount": secondary_count,
        "PrimaryCount": primary_count
        }
        family_members_list.append(members_dict)

    iRelationID = UserRelationshipModel.query.filter_by(iToUserID=iUserID,tiRelationType=1).with_entities(UserRelationshipModel.iRelationID).first()[0]
    assigned_primary = FamilyMemberRelationshipModel.query.filter_by(iRelationID = iRelationID).with_entities(FamilyMemberRelationshipModel.iFamMemID).all()
    for fam_mem in assigned_primary:	
        fam_mem_obj = FamilyMemberModel.query.filter_by(iFamMemID=fam_mem[0]).with_entities(FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName,FamilyMemberModel.dDOB,FamilyMemberModel.iUserID).all()
        for obj in fam_mem_obj:
            added_by = UserModel.query.with_entities(UserModel.vFullName).filter_by(iUserID=obj[3]).first()[0]
            members_dict = {
                "AddedBy": added_by,
                "vRelation": None,
                "vFullName" : obj[0] +" "+ obj[1],
                "dDOB": obj[2],
                "SecondaryCount": None,
                "PrimaryCount": None
              }
            family_members_list.append(members_dict)
    return family_members_list

def get_secondary_for_list(iUserID):
    secondary_for_list = []

    relations_obj = UserRelationshipModel.query.filter_by(iToUserID = iUserID,tiRelationType = 2).with_entities(UserRelationshipModel.iRelationID).all()
    for relation in relations_obj:
        iFamMemID = FamilyMemberRelationshipModel.query.filter_by(iRelationID =relation[0]).with_entities(FamilyMemberRelationshipModel.iFamMemID).first()[0]
        fam_mem_obj = FamilyMemberModel.query.filter_by(iFamMemID=iFamMemID).with_entities(FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName,FamilyMemberModel.dDOB).first()
        secondary_for_dict = {
            "dDOB" : fam_mem_obj[2],
            "vFullName" : fam_mem_obj[0] +" "+ fam_mem_obj[1]
        }
        secondary_for_list.append(secondary_for_dict)
    return secondary_for_list
