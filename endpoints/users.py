import sys
from flask import Flask, request, Blueprint, jsonify
from flask_restplus import Api, Resource, fields, reqparse, Namespace
from flask_jwt_extended import jwt_required, get_raw_jwt, get_jwt_identity,get_jwt_claims
from core import users, response

user_data = Namespace('User', description='Onboarding Operations')

device_model = user_data.model('DeviceFields',{
    'tiDeviceType' : fields.Integer(),
    'vDeviceToken' : fields.String(),
    'vDeviceUniqueID' : fields.String(),
    'vDeviceName' : fields.String(),
    'vOSVersion' : fields.String(),
    'vIPAddress' : fields.String(),
    'dcLatitude' : fields.Float(),
    'dcLongitude' : fields.Float(),
})

register_model = user_data.model('RegisterResponseFields', {
    'vEmail':  fields.String(example="test@gmail.com"), 
    'vPassword':fields.String(example="password"),
    'vFullName':fields.String(example="test test"),
    'vMobile':fields.String(example="4654532135"),
    'vCountryCode':fields.String(example="+91"),
    'dDOB': fields.Date(dt_format='rfc822',example="2018-11-11"),
    'tiGender': fields.Integer(example=0),
    'vISOLangCode':fields.String(example="en"),
})

register_response_model = user_data.model('RegisterResponse',{
  "responseMessage": fields.String(example="User Registered and OTP sent"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(register_model)
})

login_model = user_data.model('Login', {
    'vEmail': fields.String(),
    'vPassword': fields.String(),
    'DeviceData' : fields.Nested(device_model)
})

login_response_fields_model = user_data.model('LoginResponseFields',{
    'AccessToken': fields.String(example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI0ZTEyZDBjMS1lYmY1LTQ0MDgtOGZjYy1kOTI2YWY3OTE5NTgiLCJpYXQiOjE1NzcwODEyMTIsInVzZXJfY2xhaW1zIjp7InZEZXZpY2VVbmlxdWVJRCI6IjEzNTQ4OTM0In0sImZyZXNoIjpmYWxzZSwibmJmIjoxNTc3MDgxMjEyLCJ0eXBlIjoiYWNjZXNzIiwiaWRlbnRpdHkiOjUxfQ.p4dkfWHMg0KuaXehgOxX8NA2E7HlXVbkbclMo1ifJP8'),
    'vEmail': fields.String(example='sahilt.spaceo@gmail.com')
})


login_response_model = user_data.model('LoginResponse',{
  "responseMessage": fields.String(example="Login Successful"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(login_response_fields_model)
})

verify_otp_model = user_data.model('VerifyOTPFields',{
    'vEmail': fields.String(),    
    'iOTP' : fields.Integer(),
    'DeviceData' : fields.Nested(device_model)
})

verify_otp_response_model = user_data.model('VerifyOTPResponse',{
  "responseMessage": fields.String(example="OTP Verified! Login Successful"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(login_response_fields_model)
})

resend_otp_model = user_data.model('ResendOTPFields',{
    'vEmail': fields.String(),    
    'DeviceData' : fields.Nested(device_model)
})
resend_otp_response_model = user_data.model('ResendOTPResponse',{
  "responseMessage": fields.String(example="OTP Sent To Your Phone Number"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(resend_otp_model)
})

forgot_password_model = user_data.model('ForgotPasswordFields',{
    'vEmail': fields.String(example="test@gmail.com")      
})
forgot_password_response_model = user_data.model('ForgotPasswordResponse',{
  "responseMessage": fields.String(example="Reset Password Mail Sent"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(forgot_password_model)
})

update_password_model = user_data.model('UpdatePasswordFields',{
    'vEmail': fields.String(),
    'vPassword':fields.String(),      
})

update_password_response_model = user_data.model('UpdatePasswordResponse',{
  "responseMessage": fields.String(example="Password Updated Successfully"),
  "responseCode": fields.Integer(example=200),
  "responseData": fields.Nested(forgot_password_model)
})



response_model = user_data.model('CommonResponse', {
    'responseCode': fields.Integer(),
    'responseMessage': fields.String(),
})


jwt_model = user_data.model('JWT', {
    'jwt': fields.String(),
})

social_model = user_data.model('Social', {
    'token': fields.String(),
})


jwt_parser = user_data.parser()
jwt_parser.add_argument('Authorization',location='headers',default='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE1NzcxNjcyNjIsImlkZW50aXR5Ijo0OCwianRpIjoiNGZhZDczOTktMDg4Ny00YmJlLWEyZDQtOTUzZDAyZGI4ZjgyIiwiaWF0IjoxNTc3MTY3MjYyLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJ2RGV2aWNlVW5pcXVlSUQiOiJzdHJpbmcifX0.Uh2UPLCXnCj3FKRQshKi4THDGjMRB8FzXhaVhESRONY')


email_device_parser = user_data.parser()
email_device_parser.add_argument('vEmail')

verify_otp_parser = email_device_parser.copy()
verify_otp_parser.add_argument('iOTP')


@user_data.route("/Register")
class RegisterUser(Resource):
    @user_data.marshal_with(register_response_model, code=200)
    @user_data.expect(register_model)
    def post(self):
        """
        Register User
        """
        # try:
        data = request.json
        return users.register_user(data)
        # except:
        # 	return response.send_response(500,"Something went wrong",None)


@user_data.route("/Login")
class LoginUser(Resource):
    @user_data.marshal_with(login_response_model, code=200)
    @user_data.expect(login_model)
    def post(self):
        """
        Login User
        """
        # try:
        data = request.json
        return users.user_login(data)
        # except:
        # 	return response.send_response(500,"Something went wrong",None)


@user_data.route("/Social")
class LoginSocial(Resource):
    @user_data.marshal_with(response_model, code=200)
    @user_data.expect(social_model)
    def post(self):
        """
        Social Login
        """
        try:
            data = request.json
            return users.social_login(data)
        except:
            return response.send_response(500, "Something went wrong", None)


@user_data.route("/VerifyOTP")
class VerifyOTP(Resource):
    @user_data.marshal_with(verify_otp_response_model, code=200)    
    @user_data.expect(verify_otp_model)
    def post(self):
        """
        Verify OTP
        """
        # try:
        data = request.json
        return users.verify_otp(data)
        # except Exception as e:
        #     return response.send_response(409, "Something went wrong", None)


@user_data.route("/ResendOTP")
class ResendOTP(Resource):
    @user_data.marshal_with(resend_otp_response_model, code=200)       
    @user_data.expect(resend_otp_model)
    def post(self):
        """
        Resend OTP
        """
        # try:
        data = request.json
        return users.resend_otp(data)
        # except Exception as e:
        # 	return response.send_response(409,"Something went wrong",None)


@user_data.route("/ForgotPassword")
class ForgotPassword(Resource):
    @user_data.marshal_with(forgot_password_response_model, code=200)        
    @user_data.expect(forgot_password_model)
    def post(self):
        """
        Forgot Password
        """
        # try:
        data = request.json
        return users.forgot_password(data)
        # except Exception as e:
        #     return response.send_response(500, "Something went wrong", None)

@user_data.route("/UpdatePassword")
class UpdatePassword(Resource):
    @user_data.marshal_with(update_password_response_model, code=200)    
    @user_data.expect(update_password_model)
    def post(self):
        """
        Update Password
        """
        # try:
        data = request.json
        return users.update_password(data)
        # except Exception as e:
        #     return response.send_response(500, "Something went wrong", None)

 

@user_data.route("/Logout")
class UserLogoutAccess(Resource):
    @jwt_required
    @user_data.expect(jwt_parser)
    def get(self):
        """
        Logout
        """
        # try:
        iUserID = get_jwt_identity()
        vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']  
        return users.user_logout(iUserID,vDeviceUniqueID)
        # except Exception as e:
        #     return response.send_response(409, "Something went wrong", None)
