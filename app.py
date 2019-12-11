from flask import Flask, request , Blueprint 
from apis import blueprint,restplus
import config
import logging.config
from database import db

app = Flask(__name__)
log = logging.getLogger(__name__)

# restplus.init_app(app) 			### without blueprint

def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = config.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = config.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = config.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = config.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = config.RESTPLUS_ERROR_404_HELP

def main():
    configure_app(app)
    db.init_app(app)
    app.register_blueprint(blueprint, url_prefix='/api')
    app.run(debug=config.FLASK_DEBUG)


if __name__ == '__main__':
	main()
