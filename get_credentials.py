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
CLIENT_ID = os.getenv('POLLR_CLIENT_ID')
CLIENT_SECRET = os.getenv('POLLR_CLIENT_SECRET')

def get_credentials():
    credential_dir = os.getcwd()
    credential_path = os.path.join(credential_dir, 'credentials.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, SCOPES, 'http://localhost')
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
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