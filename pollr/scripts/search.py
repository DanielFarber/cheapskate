from pollr.models import Search

def run():
	searches = Search.objects.all()
	for search in searches:
		search.conduct()