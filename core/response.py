response_string = {
	'code' : None,
	'message' : None,
	'data' : None
	}

def send_response(code,message,data):
	print("Aasdad")
	response_string['code'] = code
	response_string['data'] = data
	response_string['message'] = message	
	print(response_string)
	return response_string