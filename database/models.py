from __future__ import absolute_import
from datetime import datetime
from database import db


class UserModel(db.Model):
    __tablename__ = "user_master"

    iUserID = db.Column(db.Integer, primary_key=True)
    vEmail = db.Column(db.String(45))
    vPassword = db.Column(db.String(255))
    iOTP = db.Column(db.Integer)
    tsOTPExpireAt = db.Column(db.TIMESTAMP)
    tiOTPVerified = db.Column(db.Integer,default='0')
    vCountryCode = db.Column(db.String(10))
    vUTCOffset =  db.Column(db.String(45))
    vISOLangCode = db.Column(db.String(3), default='en')
    tiIsRegistered = db.Column(db.Integer, default='1')
    tiIsDeactivated = db.Column(db.Integer, default='1') 
    vFullName = db.Column(db.String(255))
    vMobile = db.Column(db.String(20))
    dDOB = db.Column(db.Date)
    tiGender = db.Column(db.Integer)
    tsUpdatedAt = db.Column(db.TIMESTAMP ,nullable=True)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    vProfilePicURL = db.Column(db.String(255))
    tiIsSocialLogin = db.Column(db.Integer, default='0')

    def __repr__(self):
        return '<User %r>' % self.iuserid

class DeviceModel(db.Model):
    __tablename__ = "device_master"

    iDeviceId = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    tiDeviceType = db.Column(db.Integer)
    vDeviceToken = db.Column(db.String(255))
    vDeviceUniqueID = db.Column(db.String(255))
    vDeviceName = db.Column(db.String(255))
    vOSVersion = db.Column(db.String(10))
    vIPAddress = db.Column(db.String(50))
    dcLatitude = db.Column(db.DECIMAL)
    dcLongitude = db.Column(db.DECIMAL)
   
    def __repr__(self):
        return '<User %r>' % self.iDeviceId

class UserRelationshipModel(db.Model):
    __tablename__ = "user_relationship"

    iRelationID = db.Column(db.Integer, primary_key=True)
    iFromUserID = db.Column(db.Integer)
    iToUserID = db.Column(db.Integer)
    tiRelationType = db.Column(db.Integer)
    vFirstName = db.Column(db.String(45))
    vLastName = db.Column(db.String(45))
    dDOB = db.Column(db.Date)
    tiGender = db.Column(db.Integer)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class FamilyMemberModel(db.Model):
    __tablename__ = "family_member_master"

    iFamMemID = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    vRelation = db.Column(db.String(45))
    vFirstName = db.Column(db.String(45))
    vLastName = db.Column(db.String(45))
    dDOB = db.Column(db.Date)
    tiGender = db.Column(db.Integer)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class FamilyMemberRelationshipModel(db.Model):
    __tablename__ = "family_member_relationship"

    iMemRelationID = db.Column(db.Integer, primary_key=True)
    iFamMemID = db.Column(db.Integer)
    iRelationID = db.Column(db.Integer)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class SocialModel(db.Model):
    __tablename__ = "social_master"

    iSocialID = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    vSocialID = db.Column(db.String(255))
    vProfileURL = db.Column(db.String(255))
    tiSocialType = db.Column(db.Integer)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class DentistModel(db.Model):
    __tablename__ = "dentist_master"

    iDentistID = db.Column(db.Integer, primary_key=True)
    vDentistName = db.Column(db.String(45))
    tOpenTime = db.Column(db.Time)
    tCloseTime = db.Column(db.Time)
    vAddress = db.Column(db.String(255))    
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class AppointmentModel(db.Model):
    __tablename__ = "appointment_master"

    iAppointID = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    iFamMemID = db.Column(db.Integer)
    iDentistID = db.Column(db.Integer)
    dDateOfAppoint = db.Column(db.Date)
    tTimeOfAppoint = db.Column(db.Time)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class ToothEventModel(db.Model):
    __tablename__ = "tooth_event_history_master"

    iToothHisID = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    iFamMemID = db.Column(db.Integer)
    iToothID = db.Column(db.Integer)
    tiInput = db.Column(db.Integer)
    tiEvent = db.Column(db.Integer)
    tComments = db.Column(db.TEXT)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class ToothMediaModel(db.Model):
    __tablename__ = "tooth_event_media"

    iImageID = db.Column(db.Integer, primary_key=True)
    iToothHisID = db.Column(db.Integer)
    vMediaURL = db.Column(db.String(255))
    tiMediaType = db.Column(db.Integer)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class ToothStructureModel(db.Model):
    __tablename__ = "tooth_structure"    

    iToothID = db.Column(db.Integer, primary_key=True)
    iToothCategoryID = db.Column(db.Integer)
    vRightLeft = db.Column(db.String())
    vUpDown = db.Column(db.String())
    eType = db.Column(db.Enum)
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'

    iID = db.Column(db.Integer, primary_key=True)
    vToken = db.Column(db.String(255))

class ToothDiseaseModel(db.Model):
    __tablename__ = 'tooth_disease'

    iID = db.Column(db.Integer, primary_key=True)
    vTitle = db.Column(db.String())
    tContent = db.Column(db.TEXT())
    tsCreatedAt = db.Column(db.TIMESTAMP,default = datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)

class CMSPagesModel(db.Model):
    __tablename__ = 'cms_pages'

    iCMSID = db.Column(db.Integer, primary_key=True)
    vCMSTitle = db.Column(db.String())
    tContent = db.Column(db.TEXT())
    tsCreatedAt = db.Column(db.TIMESTAMP, default=datetime.now())
    tsUpdatedAt = db.Column(db.TIMESTAMP)
    new_column = db.Column(db.String())
