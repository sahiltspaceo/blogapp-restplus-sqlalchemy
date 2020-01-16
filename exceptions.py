from werkzeug.exceptions import BadRequest, MethodNotAllowed, NotAcceptable, Conflict, BadGateway
from flask_jwt_extended import JWTManager, get_jwt_identity,get_jwt_claims
from database.models import RevokedTokenModel,DeviceModel

def flask_exceptions(flask_app):
    @flask_app.errorhandler(Exception)
    def something_went_wrong(e):
        return {
            'responseMessage': "Something Went Wrong",
            'responseCode': 500,
        },500

    @flask_app.errorhandler(ValueError)
    def index_and_value(e):
        return {
            'responseMessage': "Invalid Params",
            'responseCode' : 400
        },400

    @flask_app.errorhandler(IndexError)
    def index_and_value(e):
        return {
            'responseMessage': "Invalid Params",
            'responseCode' : 400
        },400

def restplus_exceptions(restplus):
    @restplus.errorhandler(BadRequest)
    def bad_request(e):
        return {
            'responseMessage': "Bad Request",
            'responseCode': 400,
        },400

    @restplus.errorhandler(MethodNotAllowed)
    def method_not_allowed(e):
        return {
            'responseMessage': "Method Not Allowed",
            'responseCode': 405,
        },405

    @restplus.errorhandler(NotAcceptable)
    def not_acceptable(e):
        return {
            'responseMessage': "Not Acceptable",
            'responseCode': 406,
        },406

    @restplus.errorhandler(Conflict)
    def conflict(e):
        return {
            'responseMessage': "Conflict",
            'responseCode': 409,
        },409

    @restplus.errorhandler(BadGateway)
    def bad_gateway(e):
        return {
            'responseMessage': "Bad Gateway",
            'responseCode': 502,
        },502


def jwt_exceptions(jwt):

    @jwt.invalid_token_loader
    def invalid_token_response(response):
        return {
            'responseMessage': "Invalid Token",
            'responseCode': 401,
        },401

    @jwt.unauthorized_loader
    def missing_token_response(response):
        return {
            'responseMessage': "Token Missing",
            'responseCode': 401,
        },401

    @jwt.user_loader_callback_loader
    def user_loader_callback(response):
        iUserID = get_jwt_identity()
        try:
            vDeviceUniqueID = get_jwt_claims()['vDeviceUniqueID']
            if DeviceModel.query.filter_by(iUserID=iUserID, vDeviceUniqueID=vDeviceUniqueID).first() is None:
                return None
            else:
                return True
        except:
            return True

    @jwt.user_loader_error_loader
    def user_loader_error_loader(response):
        return {
            'responseMessage': "Unauthorized.",
            'responseCode': 401
        },401

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        token = decrypted_token['jti']
        query = RevokedTokenModel.query.filter_by(vToken=token).first()
        if bool(query) is True:
            return True
        else:
            return None

    @jwt.revoked_token_loader
    def blacklist_error():
        return {
            'responseMessage': "Token Has Been Revoked",
            'responseCode': 401
        },401
