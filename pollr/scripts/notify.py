from pollr.models import Searcher
from pollr.lib import gmail_service
from django import template

def run():
	service = gmail_service.get_service()
	searchers = Searcher.objects.filter(active=True)
	for searcher in searchers:
		items = searcher.all_current_items()
		if len(items) > 0:
			text = template.loader.render_to_string('notify.html', {'items': items})
			message = gmail_service.prepare_message(text, str(searcher.email))
			service.users().messages().send(userId='me', body=message).execute()
		searcher.save()