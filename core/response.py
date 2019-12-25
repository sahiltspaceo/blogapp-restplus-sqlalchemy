response_string = {
	'responseMessage' : None,
	'responseCode' : None,
	'responseData' : None
	}

def send_response(code,message,data):
	response_string['responseCode'] = code
	response_string['responseData'] = data
	response_string['responseMessage'] = message	
	print(response_string)
	return response_string