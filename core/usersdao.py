from database import db
from database.models import User

def get_users():
	user_list = []

	users = User.query.all()

	for u in users:
		user_dict = {}

		user_dict["firstname"] = u.__dict__['firstname']
		user_dict["lastname"] = u.__dict__['lastname']
		user_list.append(user_dict)

	return user_list
	
def create_user(data):
	firstname = data.get('firstname')
	lastname = data.get('lastname')
	user = User(firstname,lastname)
	db.session.add(user)
	db.session.commit()

def delete_user(firstname):
	user = User.query.filter(User.firstname == firstname).one()
	db.session.delete(user)
	db.session.commit()

