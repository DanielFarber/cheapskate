from pollr import models
from pollr.lib import gmail_service
import base64
import re

email_regex = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
service = gmail_service.get_service()

def get_message(id):
	return service.users().messages().get(userId='me', id=id).execute()

def run():
	message_list = service.users().messages().list(userId='me').execute()
	if 'messages' not in message_list: return;
	message_ids = {'ids': map(lambda m: str(m['id']), message_list['messages'])}
	messages = map(lambda m: get_message(str(m['id'])), message_list['messages'])
	parsed_messages = map(lambda m: parse_message(m), messages)
	for response in parsed_messages:
		if response['searcher'] is not None and 'active' in response:
			response['searcher'].active = response['active']
			response['searcher'].save()
	service.users().messages().batchDelete(userId='me',body=message_ids).execute();

def parse_message(msg):
	output = {}
	header_params = msg['payload']['headers']
	headers = parse_params(header_params)
	if 'From' in headers:
		output['searcher'] = models.Searcher.objects.filter(email=get_email(headers['From'])).first()
	else:
		output['searcher'] = None
	body = msg['payload']['body']
	if 'data' in body:
		lines = re.split(r'[\n\r]', base64.urlsafe_b64decode(str(body['data'])))
		parsing = parse_lines(lines)
	elif get_parts_body(msg['payload']) is not False:
		lines = re.split(r'[\n\r]', base64.urlsafe_b64decode(str(get_parts_body(msg['payload']))))
		parsing = parse_lines(lines)
	if parsing and parsing == 'active': output['active'] = True
	elif parsing and parsing == 'inactive': output['active'] = False
	return output

def get_email(txt):
	return re.findall(email_regex, txt)[0]

def parse_params(obj):
	output = {}
	for param in obj:
		output[str(param['name'])] = str(param['value'])
	return output

def get_body(body):
	pass

def get_parts_body(payload):
	if 'parts' not in payload: return False
	if len(payload['parts']) < 1: return False
	if 'body' not in payload['parts'][0]: return False
	if 'data' not in payload['parts'][0]['body']: return False
	return payload['parts'][0]['body']['data']

def parse_lines(lines):
	for line in lines:
		if re.match(r'^stop', line.lower()):
			return 'inactive'
		if re.match(r'^start', line.lower()):
			return 'active'