response_string = {
	'responseMessage' : None,
	'responseCode' : None,
	'responseData' : None
	}

error_response = {
	'responseMessage' : None,
	'responseCode' :None
}
def send_response(code,message,data):
	response_string['responseCode'] = code
	response_string['responseData'] = data
	response_string['responseMessage'] = message	
	return response_string,200

def send_error_response(code,message):
	error_response['responseCode'] = code
	error_response['responseMessage'] = message
	return error_response,code
