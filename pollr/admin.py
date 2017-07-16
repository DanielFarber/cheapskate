# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from pollr.models import Search
from pollr.models import Searcher
from pollr.models import Subscription

# Register your models here.

class SearchAdmin(admin.ModelAdmin):
	pass

class SearcherAdmin(admin.ModelAdmin):
	pass

class SubscriptionAdmin(admin.ModelAdmin):
	pass

admin.site.register(Search, SearchAdmin)

admin.site.register(Searcher, SearcherAdmin)

admin.site.register(Subscription, SubscriptionAdmin)