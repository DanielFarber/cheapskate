from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://mail.google.com'
CLIENT_ID = os.getenv('GOOGLE_API_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_API_CLIENT_SECRET')
CREDENTIALS_PATH = os.path.join(os.getcwd(), 'credentials.json')

def get_credentials():
    store = Storage(CREDENTIALS_PATH)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, SCOPES, 'http://localhost')
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + CREDENTIALS_PATH)
    return credentials

def run():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])

run()