# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from pollr.models import Search

# Register your models here.

class SearchAdmin(admin.ModelAdmin):
	pass

admin.site.register(Search, SearchAdmin)