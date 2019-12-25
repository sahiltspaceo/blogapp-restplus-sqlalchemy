from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "AC5e2b899f08ff3490d2fc910e0979e52c"
# Your Auth Token from twilio.com/console
auth_token  = "a2f4707d9275b1c35d952da79513993e"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+917567341435", 
    from_="+12055512165",
    body="Hello from Python!")

print(message.sid)