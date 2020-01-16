from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
import logging.config
import os

import endpoints
import config
from database import db, models
from flask_restplus import Api
import exceptions

app = Flask(__name__)
log = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class UserObject:
    def __init__(self, iUserID, vDeviceUniqueID):
        self.iUserID = iUserID
        self.vDeviceUniqueID = vDeviceUniqueID


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = config.FLASK_SERVER_NAME

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = config.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = config.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = config.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = config.RESTPLUS_ERROR_404_HELP

    flask_app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    flask_app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = config.JWT_BLACKLIST_TOKEN_CHECKS
    flask_app.config['JWT_BLACKLIST_ENABLED'] = config.JWT_BLACKLIST_ENABLED
    flask_app.config['JWT_HEADER_NAME'] = config.JWT_HEADER_NAME
    flask_app.config['JWT_HEADER_TYPE'] = config.JWT_HEADER_TYPE
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
    flask_app.config['TRAP_HTTP_EXCEPTIONS'] = config.TRAP_HTTP_EXCEPTIONS
    flask_app.config['ERROR_INCLUDE_MESSAGE'] = config.ERROR_INCLUDE_MESSAGE

    exceptions.flask_exceptions(flask_app)


def init_app(flask_app):
    configure_app(flask_app)
    configure_jwt(flask_app)

    blueprint = Blueprint('restplus', __name__)

    restplus = Api(
        blueprint,
        title='ToothFairy',
        version='1.0'
    )

    app.register_blueprint(blueprint, url_prefix='/API')
    restplus.add_namespace(endpoints.users)
    restplus.add_namespace(endpoints.home)
    restplus.add_namespace(endpoints.family_info)
    restplus.add_namespace(endpoints.dentist)
    restplus.add_namespace(endpoints.settings)

    exceptions.restplus_exceptions(restplus)

    db.init_app(flask_app)


def configure_jwt(flask_app):
    jwt = JWTManager(flask_app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.iUserID

    @jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return {
            'vDeviceUniqueID': user.vDeviceUniqueID
        }

    exceptions.jwt_exceptions(jwt)


def main():
    init_app(app)
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0')


if __name__ == '__main__':
    main()
