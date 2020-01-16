from __future__ import absolute_import
from database.models import (UserModel, RevokedTokenModel, DeviceModel, UserRelationshipModel,
							FamilyMemberModel,FamilyMemberRelationshipModel)
import app
import config
from app import UserObject
from flask_jwt_extended import (create_access_token)

from passlib.hash import pbkdf2_sha256 as sha256
import json
import os
import base64
from cryptography.fernet import Fernet
import datetime as dt


def is_authorized(iUserID,vDeviceUniqueID):
    if DeviceModel.query.filter_by(iUserID=iUserID,vDeviceUniqueID=vDeviceUniqueID).first() is None:
        return False
    else:
        return True

def encode_base64(data):
    return str(base64.b64encode(data.encode("utf-8")),"utf-8")

def decode_base64(data):
    return str(base64.b64decode(data), "utf-8")

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


def verify_hash(password, hashp):
    return sha256.verify(password, hashp)

def divide_list_chunks(divide_list,ItemsPerPage):
    for i in range(0, len(divide_list), ItemsPerPage):  
        yield divide_list[i:i + ItemsPerPage] 

def is_token_blacklisted(token):
    query = RevokedTokenModel.query.filter_by(vToken=token).first()
    return bool(query)


def get_tokens(iUserID, vDeviceUniqueID):
    user = UserObject(iUserID=iUserID, vDeviceUniqueID=vDeviceUniqueID)
    access_token = create_access_token(identity=user)
    return access_token

def get_cipher_key():
    file = open('cipher.key', 'rb')
    key = file.read() 
    file.close()
    key = Fernet(key)
    return key

def encrypt(data):
    encrypted = get_cipher_key().encrypt(data.encode())
    return encrypted.decode()

def decrypt(data):
    return get_cipher_key().decrypt(data.encode()).decode()
    
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

def get_user_relation_object(iRelationID):
    return UserRelationshipModel.query.filter_by(iRelationID=iRelationID).first()

def get_fullname_by_member_id(iFamMemID):
    name = FamilyMemberModel.query.filter_by(iFamMemID=iFamMemID).with_entities(FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName).first()
    vFullName = name[0] + " " + name[1]
    return vFullName

def get_offset_by_id(iUserID):
    return int(UserModel.query.filter_by(iUserID=iUserID).with_entities(UserModel.vUTCOffset).first()[0])

def get_local_datetime(iUserID,datestring):
    date_time_obj = dt.datetime.strptime(str(datestring), '%Y-%m-%d %H:%M:%S')
    utc_datetime = date_time_obj + dt.timedelta(minutes=-330)    
    client_local_datetime = utc_datetime + dt.timedelta(minutes=get_offset_by_id(iUserID)) 
    return client_local_datetime.strftime("%Y-%m-%d %H:%M:%S")

def get_own_family_members(iUserID):
    return FamilyMemberModel.query.filter_by(iUserID=iUserID).with_entities(FamilyMemberModel.iFamMemID).all()

def get_relations_from_touserid(iUserID):
    return UserRelationshipModel.query.filter_by(iToUserID = iUserID).with_entities(UserRelationshipModel.iRelationID).all()

def get_assigned_members_from_relationID(iRelationID):
    return FamilyMemberRelationshipModel.query.filter_by(iRelationID = iRelationID).with_entities(FamilyMemberRelationshipModel.iFamMemID).all()

def check_family_member_limit(iUserID):
    own_count = FamilyMemberModel.query.filter_by(iUserID=iUserID).count()
    print(iUserID)
    iRelationID = UserRelationshipModel.query.filter_by(iToUserID=iUserID,tiRelationType=1).with_entities(UserRelationshipModel.iRelationID).first()
    if iRelationID is not None:
        assigned_count = FamilyMemberRelationshipModel.query.filter_by(iRelationID = iRelationID[0]).count()
    else:
        assigned_count = 0

    if own_count + assigned_count < config.MAX_FAMILY_MEMBER_LIMIT:
        return True
    else:
        return False

def get_user_dict(iUserID):
    db_obj = UserModel.query.with_entities(UserModel.dDOB,UserModel.vFullName,UserModel.iUserID).filter_by(iUserID=iUserID).first()
    user_dict = {
        "PK" : encrypt(str(db_obj[2])),
        "dDOB" : db_obj[0],
        "vFullName" : db_obj[1]
    }
    return user_dict

def get_primary_list(iUserID):
    primary_list = []
    db_obj =  UserRelationshipModel.query.filter_by(iFromUserID = iUserID,tiRelationType=1).with_entities(UserRelationshipModel.dDOB,UserRelationshipModel.vFirstName,UserRelationshipModel.vLastName,UserRelationshipModel.iRelationID).all()
    for obj in db_obj:
        primary_dict = {
            "PK" : encrypt(str(obj[3])),
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
        relations = FamilyMemberRelationshipModel.query.filter_by(iFamMemID =iFamMemID).with_entities(FamilyMemberRelationshipModel.iRelationID).all()

        if len(relations) != 0:
            for relations_id in relations:
                primary_count = UserRelationshipModel.query.filter_by(iRelationID = relations_id[0],tiRelationType = 1).count()
                secondary_count = UserRelationshipModel.query.filter_by(iRelationID = relations_id[0],tiRelationType = 2).count()
        else:
            primary_count = 0
            secondary_count = 0

        members_dict = {
            "iFamMemID" : encrypt(str(iFamMemID)),
            "AddedBy": None,
            "vRelation": obj[4],
            "vFullName": obj[1] +" "+ obj[2],
            "dDOB": obj[3],
            "SecondaryCount": secondary_count,
            "PrimaryCount": primary_count
        }
        family_members_list.append(members_dict)

    relations_obj = UserRelationshipModel.query.filter_by(iToUserID=iUserID,tiRelationType=1).with_entities(UserRelationshipModel.iRelationID).all()
    for relation in relations_obj:
        assigned_primary = FamilyMemberRelationshipModel.query.filter_by(iRelationID = relation[0]).with_entities(FamilyMemberRelationshipModel.iFamMemID).first()
        if assigned_primary is not None:
            fam_mem_obj = FamilyMemberModel.query.filter_by(iFamMemID=assigned_primary[0]).with_entities(FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName,FamilyMemberModel.dDOB,FamilyMemberModel.iUserID).first()
            added_by = UserModel.query.with_entities(UserModel.vFullName).filter_by(iUserID=fam_mem_obj[3]).first()[0]
            members_dict = {
                "AddedBy": added_by,
                "vRelation": None,
                "vFullName" : fam_mem_obj[0] +" "+ fam_mem_obj[1],
                "dDOB": fam_mem_obj[2],
                "SecondaryCount": None,
                "PrimaryCount": None
              }
            family_members_list.append(members_dict)
    return family_members_list

def get_secondary_for_list(iUserID):
    secondary_for_list = []

    relations_obj = UserRelationshipModel.query.filter_by(iToUserID = iUserID,tiRelationType = 2).with_entities(UserRelationshipModel.iRelationID).all()
    for relation in relations_obj:
        print(relation)
        iFamMemID = FamilyMemberRelationshipModel.query.filter_by(iRelationID =relation[0]).with_entities(FamilyMemberRelationshipModel.iFamMemID).first()
        if iFamMemID is not None:
            fam_mem_obj = FamilyMemberModel.query.filter_by(iFamMemID=iFamMemID[0]).with_entities(FamilyMemberModel.vFirstName,FamilyMemberModel.vLastName,FamilyMemberModel.dDOB).first()
            secondary_for_dict = {
                "PK" : encrypt(str(iFamMemID[0])),
                "dDOB" : fam_mem_obj[2],
                "vFullName" : fam_mem_obj[0] +" "+ fam_mem_obj[1]
            }
            secondary_for_list.append(secondary_for_dict)
    return secondary_for_list

def check_assign_limit(iFamMemID,tiRelationType):
    db_obj = FamilyMemberRelationshipModel.query.filter_by(iFamMemID=iFamMemID).with_entities(FamilyMemberRelationshipModel.iRelationID).all()    
    counter = 0
    
    for obj in db_obj:
        relation_type = UserRelationshipModel.query.filter_by(iRelationID=obj[0]).with_entities(UserRelationshipModel.tiRelationType).first()[0]
        if relation_type == tiRelationType:
            counter = counter + 1 
    if not counter < 2:
        return False
    else:
        return True
