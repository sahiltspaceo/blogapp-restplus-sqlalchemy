import facebook

def get_social(token,social_type):
	if social_type == 1:
		graph = facebook.GraphAPI(access_token=token, version="3.1")
		args = {'fields' : 'id,name,email,picture,birthday,gender'}
		profile = graph.get_object('me', **args)
		return profile
