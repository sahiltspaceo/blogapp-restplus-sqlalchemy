import sys
from flask import Flask, request , Blueprint ,jsonify
from flask_restplus import Api, Resource, fields, reqparse,Namespace
from core import usersdao,response
from database.models import User

sys.path.append(".")


user_data = Namespace('users',description='All user related operations')

user_model = user_data.model('User',{
		'firstname':fields.String(required = False,description = 'First Name of user',help = 'Fist Name cannot be blank'),
		'lastname':fields.String(required = True,description = 'Last Name of user',help = 'Last Name cannot be blank')
})
response_model = user_data.model('ApiResponse',{
		'code':fields.Integer(required = True,example = "200"),
		'data':fields.String(),
		'message':fields.String(required = True,example = "Success String"),
})

@user_data.route("/")
class UserClass(Resource):
	@user_data.marshal_with(response_model, envelope='ApiResponse' ,code=200)
	def get(self):
		"""
        get all users
        """
		try:
			user_list = usersdao.get_users()
			return response.send_response(200,"Users List",user_list)
		except Exception as e:
			return response.send_response(409,"Could not retrieve information",None)

	@user_data.marshal_with(response_model, envelope='ApiResponse' ,code=200)
	@user_data.expect(user_model)		
	def post(self):
		"""
		Create User
		"""
		data = request.json
		usersdao.create_user(data)
		return response.send_response(200,"User Created",None)


		
@user_data.route("/delete/<firstname>")
class UserDelete(Resource):
	@user_data.marshal_with(response_model, envelope='ApiResponse' ,code=200)
	def delete(self,firstname):
		"""
        delete user by firstname
        """	
		usersdao.delete_user(firstname)
		return response.send_response(200,"User Deleted",None)
	
		# try:
		# 	return users.delete(username)
		# except Exception as e:
		# 	return response.send_response(409,"Could not retrieve information",None)

	
