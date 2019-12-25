from __future__ import absolute_import
from datetime import datetime
from database import db
import config


class UserModel(db.Model):
    __tablename__ = "user_master"

    iUserID = db.Column(db.Integer, primary_key=True)
    vEmail = db.Column(db.String(45))
    vPassword = db.Column(db.String(255))
    iOTP = db.Column(db.Integer)
    tsOTPExpireAt = db.Column(db.TIMESTAMP)
    tiOTPVerified = db.Column(db.Integer,default='0')
    vCountryCode = db.Column(db.String(10))
    vISOLangCode = db.Column(db.String(3), default='en')
    tiIsRegistered = db.Column(db.Integer, default='1')
    tiIsDeactivated = db.Column(db.Integer, default='1') 
    vFullName = db.Column(db.String(255))
    vMobile = db.Column(db.String(20))
    dDOB = db.Column(db.Date)
    tiGender = db.Column(db.Integer)
    dtUpdatedAt = db.Column(db.DATETIME ,nullable=True)
    dtCreatedAt = db.Column(db.DATETIME,default = datetime.now())
    vProfilePicURL = db.Column(db.String(255))

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
    dtUpdatedAt = db.Column(db.DATETIME)
    dtCreatedAt = db.Column(db.DATETIME,default = datetime.now())

class FamilyMemberModel(db.Model):
    __tablename__ = "family_member_master"

    iFamMemID = db.Column(db.Integer, primary_key=True)
    iUserID = db.Column(db.Integer)
    vRelation = db.Column(db.String(45))
    vFirstName = db.Column(db.String(45))
    vLastName = db.Column(db.String(45))
    dDOB = db.Column(db.Date)
    tiGender = db.Column(db.Integer)
    dtUpdatedAt = db.Column(db.DATETIME)
    dtCreatedAt = db.Column(db.DATETIME,default = datetime.now())

class FamilyMemberRelationshipModel(db.Model):
    __tablename__ = "family_member_relationship"

    iMemRelationID = db.Column(db.Integer, primary_key=True)
    iFamMemID = db.Column(db.Integer)
    iRelationID = db.Column(db.Integer)
    dtUpdatedAt = db.Column(db.DATETIME)
    dtCreatedAt = db.Column(db.DATETIME,default = datetime.now())
    
class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'

    iid = db.Column(db.Integer, primary_key=True)
    vtoken = db.Column(db.String(255))
