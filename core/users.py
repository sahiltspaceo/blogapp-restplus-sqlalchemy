from __future__ import absolute_import
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import datetime
import os
import app
from app import UserObject
import json

from database import db
from database.models import UserModel, RevokedTokenModel, DeviceModel
from . import response, sendemail, generateotp
from .utils import (get_lang_json, is_authorized,find_by_email,
                    find_by_userid,find_id_by_email,generate_hash,
                    verify_hash,is_token_blacklisted,get_access_token)

import time
def get_users():
    def to_json(x):
        users_list = []
        return {
            'id': x.iUserID,
            'email': x.vEmail,
        }
    users_list = list(map(lambda x: to_json(x), UserModel.query.all()))
    return users_list




def register_user(data):
    current_user = find_by_email(data['vEmail'])
    lang_response = get_lang_json(data['vISOLangCode'])


    if current_user is not None and current_user.tiIsRegistered == 1:
        return response.send_response(400, 'User Already Exists', None)


    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_response(400, lang_response['onboarding']['account_deactivated'], None)

   
    elif current_user is not None and current_user.tiIsRegistered == 0:
        new_user = db.session.query(UserModel).filter(
            UserModel.vEmail == data['vEmail']).one()
        new_user.vPassword = generate_hash(data['vPassword'])
        new_user.iOTP = generateotp.generateOTP()
        new_user.tsOTPExpireAt = datetime.datetime.now() + datetime.timedelta(minutes=5)
        new_user.tiIsRegistered = 1

    else:
        new_user = UserModel(
            vEmail=data['vEmail'],
            vPassword=generate_hash(data['vPassword']),
            iOTP=generateotp.generateOTP(),
            tsOTPExpireAt=datetime.datetime.now() + datetime.timedelta(minutes=5),
            tiOTPVerified=0
        )
        db.session.add(new_user)

    db.session.commit()
    db.session.flush()

    return response.send_response(200, lang_response['onboarding']['registered_and_otp_sent'], data)


def user_login(data):
    current_user = find_by_email(data['vEmail'])
    device_unique_id = data['DeviceData']['vDeviceUniqueID']

    if current_user is None or (current_user is not None and current_user.tiIsRegistered == 0):
        return response.send_response(400, 'User Not Registered', None)

    if current_user is not None:
        lang_response = get_lang_json(current_user.vISOLangCode)

    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_response(400, lang_response['onboarding']['account_deactivated'], None)

    userid = find_id_by_email(data['vEmail'])

    if verify_hash(data['vPassword'], current_user.vPassword):
        if current_user.tiOTPVerified == 0:
            current_user.iOTP=generateotp.generateOTP()
            current_user.tsOTPExpireAt=datetime.datetime.now() + datetime.timedelta(minutes=5)
            db.session.commit()
            db.session.flush()
            return response.send_response(200, lang_response['onboarding']['otp_sent'], None)
        
        if is_authorized(userid,device_unique_id):
            user = UserObject(iUserID=userid, vDeviceUniqueID=device_unique_id)
            access_token = create_access_token(identity=user)

            login_response = {
                'vEmail': data['vEmail'],
                'AccessToken': access_token,
            }            
            return response.send_response(200, lang_response['onboarding']['login_success'], login_response)
        else:
            new_device = DeviceModel.query.filter_by(iUserID=userid).first()
            if new_device is not None:
                new_device.vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
            else:
                new_device = DeviceModel(
                    iUserID = userid,
                    vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
                )
            db.session.add(new_device)
            db.session.commit()
            db.session.flush()

            user = UserObject(iUserID=userid, vDeviceUniqueID=device_unique_id)
            access_token = create_access_token(identity=user)

            login_response = {
                'vEmail': data['vEmail'],
                'AccessToken': access_token,
            }
            return response.send_response(200, lang_response['onboarding']['login_success'], login_response)

    else:
        return response.send_response(400, lang_response['onboarding']['invalid_password'], None)


def user_logout(iUserID,vDeviceUniqueID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    if not is_authorized(iUserID,vDeviceUniqueID):
        return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

    DeviceModel.query.filter_by(iUserID=iUserID).delete()
    db.session.commit()
    return response.send_response(200, lang_response['onboarding']['logout_success'], None)
   

def forgot_password(data):
    current_user = find_by_email(data['vEmail'])

    if current_user is None or (current_user is not None and current_user.tiIsRegistered == 0):
        return response.send_response(400, 'User Not Registered', None)

    if current_user is not None:
        lang_response = get_lang_json(current_user.vISOLangCode)

    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_response(400, lang_response['onboarding']['account_deactivated'], None)

    otp = generateotp.generateOTP()
    
    if sendemail.send_mail(data['vEmail'], otp):
        new_user = db.session.query(UserModel).filter(UserModel.vEmail == data['vEmail']).one()
        new_user.iOTP = otp
        new_user.tsOTPExpireAt = datetime.datetime.now() + datetime.timedelta(minutes=5)
        db.session.commit()
        db.session.flush()
        return response.send_response(200, lang_response['onboarding']['reset_pw_mail_sent'], None)
    else:
        return response.send_response(400, lang_response['onboarding']['mail_sending_fail'], None)


def update_password(data):
    current_user = find_by_email(data['vEmail'])
    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)

    current_user.vPassword = generate_hash(data['vPassword'])
    db.session.commit()
    db.session.flush()
    return response.send_response(200, lang_response['onboarding']['password_updated'],{'vEmail': data['vEmail']})   ## Forgot password Email OTP verification


def verify_otp(data):
    current_user = find_by_email(data['vEmail'])
    vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
    otp = data['iOTP']

    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)


    if (datetime.datetime.now() < current_user.tsOTPExpireAt):
        if current_user.iOTP == int(otp):
            if current_user.tiOTPVerified != 1:
                access_token = get_access_token(find_id_by_email(data['vEmail']),vDeviceUniqueID)
                token_response = {
                    'vEmail': data['vEmail'],
                    'AccessToken': access_token,
                    'DeviceData': data
                }
                current_user.tiOTPVerified = 1
                current_user.iOTP = None
                current_user.tsOTPExpireAt = None

                new_device = DeviceModel(
                        iUserID = find_id_by_email(data['vEmail']),
                        vDeviceUniqueID = vDeviceUniqueID
                    )
                db.session.add(new_device)           
                db.session.commit()
                return response.send_response(200, lang_response['onboarding']['otp_login_success'], token_response)
            else:
                current_user.iOTP = None
                current_user.tsOTPExpireAt = None
                db.session.commit()
                return response.send_response(200, lang_response['onboarding']['otp_verified'],{'vEmail': data['vEmail']})   ## Forgot password Email OTP verification
            # if (DeviceModel.query.filter_by(iUserID=find_id_by_email(data['vEmail'])).first()) and (not is_authorized(find_id_by_email(data['vEmail']),vDeviceUniqueID)):
            #     db.session.rollback()
            #     return response.send_response(203, lang_response['onboarding']['unauthorized'], None)
            
        else:
            return response.send_response(400, lang_response['onboarding']['incorrect_otp'], None)
    else:
        return response.send_response(400, lang_response['onboarding']['otp_expired'], None)


def resend_otp(data):
    current_user = find_by_email(data['vEmail'])
    vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
    
    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)
    
    try:
        otp = generateotp.generateOTP()
        now = datetime.datetime.now()
        now_plus_5 = now + datetime.timedelta(minutes=5)

        current_user.iOTP = int(otp)
        current_user.tsOTPExpireAt = now_plus_5
        db.session.commit()

        # if (DeviceModel.query.filter_by(iUserID=find_id_by_email(data['vEmail'])).first()) and (not is_authorized(find_id_by_email(data['vEmail']),vDeviceUniqueID)):
        #     db.session.rollback()
        #     return response.send_response(203, lang_response['onboarding']['unauthorized'], None)

        return response.send_response(200, lang_response['onboarding']['otp_sent'], {'email':data['vEmail']})
    except:
        return response.send_response(400, lang_response['onboarding']['error_sending_otp'], None)

