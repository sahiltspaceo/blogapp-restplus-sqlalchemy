from __future__ import absolute_import
import datetime


from database import db
from database.models import UserModel, DeviceModel , SocialModel,RevokedTokenModel
from . import response, sendemail, generateotp
from .utils import (get_lang_json, is_authorized,find_by_email,
                    find_by_userid,find_id_by_email,generate_hash,
                    verify_hash,get_tokens)
from .social import get_social



def register_user(data):
    current_user = find_by_email(data['vEmail'])
    lang_response = get_lang_json(data['vISOLangCode'])


    if current_user is not None and current_user.tiIsRegistered == 1:
        return response.send_error_response(400, 'User Already Exists')


    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_error_response(401, lang_response['onboarding']['account_deactivated'])

   
    elif current_user is not None and current_user.tiIsRegistered == 0:
        new_user = db.session.query(UserModel).filter(
            UserModel.vEmail == data['vEmail']).one()
        new_user.vPassword = generate_hash(data['vPassword'])
        new_user.iOTP = generateotp.generateOTP()
        new_user.tsOTPExpireAt = datetime.datetime.now() + datetime.timedelta(minutes=5)
        new_user.vFullName = data['vFullName']
        new_user.vMobile = data['vMobile']
        new_user.vCountryCode = data['vCountryCode']
        new_user.dDOB = data['dDOB']
        new_user.tiGender = data['tiGender']
        new_user.vISOLangCode = data['vISOLangCode']
        new_user.vProfilePicURL = data['vProfilePicURL'].replace(" ","%") + "_" + str(datetime.datetime.now())
        new_user.vUTCOffset = data['vUTCOffset']

    else:
        new_user = UserModel(
            vEmail=data['vEmail'],
            vPassword=generate_hash(data['vPassword']),
            iOTP=generateotp.generateOTP(),
            vFullName = data['vFullName'],
            vMobile = data['vMobile'],
            vCountryCode = data['vCountryCode'],
            dDOB = data['dDOB'],
            tiGender = data['tiGender'],
            vISOLangCode = data['vISOLangCode'],
            vProfilePicURL = data['vProfilePicURL'].replace(" ","%") + "_" + str(datetime.datetime.now()),
            vUTCOffset = data['vUTCOffset'],
            tsOTPExpireAt=datetime.datetime.now() + datetime.timedelta(minutes=5),
            tiOTPVerified=0
        )
        db.session.add(new_user)

    db.session.commit()

    return response.send_response(200, lang_response['onboarding']['registered_and_otp_sent'], data)

def user_login(data):
    current_user = find_by_email(data['vEmail'])

    if current_user is None or (current_user is not None and current_user.tiIsRegistered == 0):
        return response.send_error_response(404, 'User Not Registered')

    if current_user is not None:
        lang_response = get_lang_json(current_user.vISOLangCode)

    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_error_response(401, lang_response['onboarding']['account_deactivated'])

    iUserID = find_id_by_email(data['vEmail'])

    if verify_hash(data['vPassword'], current_user.vPassword):
        if current_user.tiOTPVerified == 0:
            current_user.iOTP = generateotp.generateOTP()
            current_user.tsOTPExpireAt=datetime.datetime.now() + datetime.timedelta(minutes=5)
            db.session.commit()
            return response.send_response(200, lang_response['onboarding']['otp_sent'], None)
        
        if is_authorized(iUserID,data['DeviceData']['vDeviceUniqueID']):
            login_response = {
                'vEmail': data['vEmail'],
                'AccessToken': get_tokens(iUserID=iUserID, vDeviceUniqueID=data['DeviceData']['vDeviceUniqueID']),
            }            
            return response.send_response(200, lang_response['onboarding']['login_success'], login_response)
        else:
            new_device = DeviceModel.query.filter_by(iUserID=iUserID).first()
            if new_device is not None:
                new_device.vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
            else:
                new_device = DeviceModel(
                    iUserID = iUserID,
                    tiDeviceType = data['DeviceData']['tiDeviceType'],
                    vDeviceToken = data['DeviceData']['vDeviceToken'],
                    vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID'],
                    vDeviceName = data['DeviceData']['vDeviceName'],
                    vOSVersion = data['DeviceData']['vOSVersion']
                )
            db.session.add(new_device)
            db.session.commit()

            login_response = {
                'vEmail': data['vEmail'],
                'AccessToken': get_tokens(iUserID=iUserID, vDeviceUniqueID=data['DeviceData']['vDeviceUniqueID']),
            }
            return response.send_response(200, lang_response['onboarding']['login_success'], login_response)

    else:
        return response.send_error_response(400, lang_response['onboarding']['invalid_password'])

   

def forgot_password(data):
    current_user = find_by_email(data['vEmail'])

    if current_user is None or (current_user is not None and current_user.tiIsRegistered == 0):
        return response.send_error_response(400, 'User Not Registered')

    if current_user is not None:
        lang_response = get_lang_json(current_user.vISOLangCode)

    if current_user is not None and current_user.tiIsDeactivated == 0:
        return response.send_error_response(401, lang_response['onboarding']['account_deactivated'])

    otp = generateotp.generateOTP()
    
    if sendemail.send_mail(data['vEmail'], otp):
        new_user = db.session.query(UserModel).filter(UserModel.vEmail == data['vEmail']).one()
        new_user.iOTP = otp
        new_user.tsOTPExpireAt = datetime.datetime.now() + datetime.timedelta(minutes=5)
        db.session.commit()
        return response.send_response(200, lang_response['onboarding']['reset_pw_mail_sent'], data['vEmail'])
    else:
        return response.send_error_response(400, lang_response['onboarding']['mail_sending_fail'])



def verify_otp(data):
    current_user = find_by_email(data['vEmail'])
    vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID']
    otp = data['iOTP']

    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)

    if datetime.datetime.now() < current_user.tsOTPExpireAt:
        if current_user.iOTP == int(otp):
            if current_user.tiOTPVerified != 1:
                
                token_response = {
                    'vEmail': data['vEmail'],
                    'AccessToken': get_tokens(iUserID=find_id_by_email(data['vEmail']), vDeviceUniqueID=vDeviceUniqueID),
                }
                current_user.tiOTPVerified = 1
                current_user.iOTP = None
                current_user.tsOTPExpireAt = None

                new_device = DeviceModel(
                        iUserID = find_id_by_email(data['vEmail']),
                        tiDeviceType = data['DeviceData']['tiDeviceType'],
                        vDeviceToken = data['DeviceData']['vDeviceToken'],
                        vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID'],
                        vDeviceName = data['DeviceData']['vDeviceName'],
                        vOSVersion = data['DeviceData']['vOSVersion']
                    )
                
                db.session.add(new_device)           
                db.session.commit()
                return response.send_response(200, lang_response['onboarding']['otp_login_success'], token_response)
            else:
                ### Forgot Password Email OTP Verification
                current_user.iOTP = None
                current_user.tsOTPExpireAt = None
                db.session.commit()
                return response.send_response(200, lang_response['onboarding']['otp_verified'],{'vEmail': data['vEmail']})   ## Forgot password Email OTP verification
        else:
            return response.send_error_response(400, lang_response['onboarding']['incorrect_otp'])
    else:
        return response.send_error_response(400, lang_response['onboarding']['otp_expired'])


def resend_otp(data):
    current_user = find_by_email(data['vEmail'])
    
    if current_user:
        lang_response = get_lang_json(current_user.vISOLangCode)
    else:
        return response.send_error_response(400, 'User Not Registered')

    try:
        otp = generateotp.generateOTP()
        now = datetime.datetime.now()
        now_plus_5 = now + datetime.timedelta(minutes=5)

        current_user.iOTP = int(otp)
        current_user.tsOTPExpireAt = now_plus_5
        db.session.commit()

        return response.send_response(200, lang_response['onboarding']['otp_sent'], {'email':data['vEmail']})
    except:
        return response.send_error_response(400, lang_response['onboarding']['error_sending_otp'])


def social_login(data):
    social_response = get_social(token = data['AccessToken'],social_type=data['tiSocialType'])
    if 'email' not in social_response.keys():
        return response.send_error_response(400, "Could Not Get Email")
    else:
        gender = social_response.get("gender",None)
        if gender is not None:
            gender = 1 if social_response['gender'] == 'male' else 2

        new_user = UserModel(
            vEmail = social_response['email'],
            vFullName = social_response.get("name",None),
            tiGender = gender,
            dDOB = social_response.get("birthday",None),
            vProfilePicURL = social_response.get('picture', None).get('data',None).get('url',None),
            tiIsSocialLogin = 1,
            tiIsRegistered = 1,
            tiOTPVerified = 1,
            vUTCOffset = data['vUTCOffset']
        )
        db.session.add(new_user)
        db.session.commit()
        db.session.flush()
        iUserID = new_user.iUserID

        new_device = DeviceModel(
            iUserID = iUserID,
            tiDeviceType = data['DeviceData']['tiDeviceType'],
            vDeviceToken = data['DeviceData']['vDeviceToken'],
            vDeviceUniqueID = data['DeviceData']['vDeviceUniqueID'],
            vDeviceName = data['DeviceData']['vDeviceName'],
            vOSVersion = data['DeviceData']['vOSVersion']
        )
        db.session.add(new_device)

        new_social = SocialModel(
            iUserID = iUserID,
            vSocialID = social_response.get("id",None),
            tiSocialType = data['tiSocialType']
        )
        db.session.add(new_social)

        db.session.commit()

        login_response = {
            'vEmail': social_response['email'],
            'AccessToken': get_tokens(iUserID=iUserID, vDeviceUniqueID=data['DeviceData']['vDeviceUniqueID'])
        }

        lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)            
        return response.send_response(200, lang_response['onboarding']['login_success'], login_response)