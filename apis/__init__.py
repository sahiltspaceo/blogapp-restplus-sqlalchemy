from flask_restplus import Api
from flask import Blueprint
from flask_restplus import Api


from .users import user_data as users

blueprint = Blueprint('restplus', __name__)

restplus = Api(
	blueprint,
    title='My Blog',
    version='1.0',
    description='A description',
)

restplus.add_namespace(users)