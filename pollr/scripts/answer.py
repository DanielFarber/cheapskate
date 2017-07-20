from pollr import models
from pollr.lib import gmail_service
import base64
import re
from IPython import embed
email_regex = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
service = gmail_service.get_service()

def get_message(id):
	return service.users().messages().get(userId='me', id=id).execute()

def run():
	message_list = service.users().messages().list(userId='me').execute()
	messages = map(lambda m: get_message(str(m['id'])), message_list['messages'])
	parsed_messages = map(lambda m: parse_message(m), messages)
	print(parsed_messages)

def parse_message(msg):
	output = {}
	headers = get_headers(msg)
	try:
		output['from'] = get_email(headers['From'])
	except:
		continue
	return output

def get_email(txt):
	return re.findall(email_regex, txt)[0]

def get_headers(msg):
	headers = {}
	for header in msg['payload']['headers']:
		headers[str(header['name'])] = str(header['value'])
	return headers

