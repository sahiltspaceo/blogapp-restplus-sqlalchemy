from flask import request
from flask_restplus import  Resource, fields, Namespace
from core import users

user_data = Namespace('User', description='Onboarding Operations')

device_model = user_data.model('DeviceFields',{
    'tiDeviceType' : fields.Integer(),
    'vDeviceToken' : fields.String(),
    'vDeviceUniqueID' : fields.String(),
    'vDeviceName' : fields.String(),
    'vOSVersion' : fields.String()
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
    'vProfilePicURL' : fields.String(),
    'vUTCOffset' : fields.String(example='+330')
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
    'AccessToken': fields.String(example='<JWT>'),
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
    'vEmail': fields.String()    
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

response_model = user_data.model('CommonResponse', {
    'responseCode': fields.Integer(),
    'responseMessage': fields.String(),
})

jwt_model = user_data.model('JWT', {
    'jwt': fields.String(),
})

social_model = user_data.model('Social', {
    'AccessToken': fields.String(),
    'tiSocialType' : fields.Integer(description ='1 - Facebook, 2 - Apple'),
    'DeviceData' : fields.Nested(device_model),
    'vUTCOffset': fields.String()

})
social_login_response  = user_data.model('SocialLoginResponse',{
      "responseMessage": fields.String(example="Login Successful"),
      "responseCode": fields.Integer(example=200),
      "responseData": fields.Nested(login_response_fields_model)
})
error_response = user_data.model('ErrorResponse',{
    "responseMessage": fields.String(example="Error Message"),
    "responseCode": fields.Integer(example=400),
})

jwt_parser = user_data.parser()
jwt_parser.add_argument('JWTAuth',location='headers')


@user_data.route("/Register")
class RegisterUser(Resource):
    @user_data.response(200,"User Registered And Otp Sent",register_response_model)
    @user_data.response(400,"User Already Exists",error_response)
    @user_data.response(401,"Account Has Been Deactivated",error_response)
    @user_data.expect(register_model)
    def post(self):
        """
        Register User
        """
        data = request.json
        return users.register_user(data)
    

@user_data.route("/Login")
class LoginUser(Resource):
    @user_data.response(200,"Login Success",login_response_model)
    @user_data.response(404,"User Not Registered",error_response)
    @user_data.response(401,"Account Has Been Deactivated",error_response)
    @user_data.expect(login_model)
    def post(self):
        """
        Login User
        """
        data = request.json
        return users.user_login(data)


@user_data.route("/VerifyOTP")
class VerifyOTP(Resource):
    @user_data.response(200,"OTP Verified! Login Successful",verify_otp_response_model)
    @user_data.response(400,"Incorrect OTP. Try Again",error_response)
    @user_data.expect(verify_otp_model)
    def post(self):
        """
        Verify OTP
        """
        data = request.json
        return users.verify_otp(data)


@user_data.route("/ResendOTP")
class ResendOTP(Resource):
    @user_data.response(200,"OTP Sent",resend_otp_response_model)
    @user_data.response(400,"Error Sending OTP",error_response)
    @user_data.expect(resend_otp_model)
    def post(self):
        """
        Resend OTP
        """
        data = request.json
        return users.resend_otp(data)


@user_data.route("/ForgotPassword")
class ForgotPassword(Resource):
    @user_data.response(200,"Mail Sent",forgot_password_response_model)
    @user_data.response(400,"Error Sending Mail",error_response)
    @user_data.expect(forgot_password_model)
    def post(self):
        """
        Forgot Password
        """
        data = request.json
        return users.forgot_password(data)


@user_data.route("/SocialLogin")
class SocialLogin(Resource):
    @user_data.response(200,"Login Successful",social_login_response)
    @user_data.response(400,"Could Not Get Email",error_response)
    @user_data.response(401,"Account Has Been Deactivated",error_response)
    @user_data.expect(social_model)
    def post(self):
        """
        Social Login 
        """
        data = request.json
        return users.social_login(data)
