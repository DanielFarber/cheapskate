import os
import base64
import httplib2
import sys
import json as JSON
from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from email.mime.text import MIMEText

def get_service():
	scope = 'https://mail.google.com'
	client_id = os.getenv('GOOGLE_API_CLIENT_ID')
	client_secret = os.getenv('GOOGLE_API_CLIENT_SECRET')
	credentials_path = os.path.join('/'.join(__file__.split('/')[0:-3]), 'credentials.json')

	flow = OAuth2WebServerFlow(client_id, client_secret, scope)
	storage = Storage(credentials_path)
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		return false

	http = credentials.authorize(httplib2.Http())
	service = build('gmail', 'v1', http=http)
	return service

def prepare_message(message, recipient):
	message = MIMEText(message, 'html')
	message['to'] = recipient
	encoded_text = base64.urlsafe_b64encode(message.as_string())
	return {'raw': encoded_text}