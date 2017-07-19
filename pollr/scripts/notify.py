from pollr.models import Searcher
from pollr.lib import gmail_service

def run():
	service = gmail_service.get_service()
	searchers = Searcher.objects.all()
	for searcher in searchers:
		items = searcher.all_current_items()
		if len(items) > 0:
			text = "\n".join(items)
			message = gmail_service.prepare_message(text, str(searcher.email))
			service.users().messages().send(userId='me', body=message).execute()
		searcher.save()