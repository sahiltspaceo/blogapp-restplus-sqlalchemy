from flask import Flask, request, Blueprint
from flask_jwt_extended import JWTManager, get_jwt_identity,get_jwt_claims
import logging.config
import os

import endpoints
import config
from database import db, models
from core import users
from flask_restplus import Api


app = Flask(__name__)
log = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class UserObject:
    def __init__(self, iUserID, vDeviceUniqueID):
        self.iUserID = iUserID
        self.vDeviceUniqueID = vDeviceUniqueID

# restplus.init_app(app)            ### without blueprint


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = config.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = config.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = config.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = config.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = config.RESTPLUS_ERROR_404_HELP

    flask_app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
    flask_app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES
    flask_app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = config.JWT_BLACKLIST_TOKEN_CHECKS
    flask_app.config['JWT_BLACKLIST_ENABLED'] = config.JWT_BLACKLIST_ENABLED


def init_app(flask_app):
    configure_app(app)
    configure_jwt(app)

    blueprint = Blueprint('restplus', __name__)
    restplus = Api(
        blueprint,
        title='ToothFairy',
        version='1.0',
    )
    app.register_blueprint(blueprint, url_prefix='/api')
    restplus.add_namespace(endpoints.users)
    restplus.add_namespace(endpoints.family_info)

    db.init_app(app)


def configure_jwt(app):
    jwt = JWTManager(app)       

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.iUserID

    @jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return {
            'vDeviceUniqueID' : user.vDeviceUniqueID
        }

    @jwt.invalid_token_loader
    def invalid_token_response(response):
        return {
            'responseMessage' : "Invalid Token",
            'responseCode' : 203,
        }

    @jwt.unauthorized_loader
    def missing_token_response(response):
        return {
            'responseMessage' : "Token Missing",
            'responseCode' : 203,
        }


def main():
    init_app(app)
    app.run(debug=config.FLASK_DEBUG)


if __name__ == '__main__':
    main()
