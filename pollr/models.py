# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup as bsoup
import pytz
import httplib2

class Search(models.Model):
	id = models.AutoField(primary_key=True)
	locale = models.CharField(max_length=255, default='newyork')
	path = models.CharField(max_length=255, default='/search/ss')
	name = models.CharField(max_length=255, unique=True)
	items = models.ManyToManyField('Item', through='Hit')
	def __str__(self):
		return self.name
	class Meta:
		verbose_name_plural = 'Searches'
		unique_together = (('path', 'locale'))
	def conduct(self):
		url = str('https://' + str(self.locale) + '.craigslist.org' + str(self.path))
		(headers, html) = httplib2.Http().request(str(url))
		soup = bsoup(html, 'html.parser')
		for li in soup.find_all('li', {'class': 'result-row'}):
			anchor = li.find_all('a')[1]
			item = Item.getsert(anchor['data-id'], anchor['href'], anchor.text)
			Hit.passert(item, self)

class Item(models.Model):
	id = models.AutoField(primary_key=True)
	cl_id = models.TextField(max_length=255, unique=True, null=True)
	url = models.CharField(max_length=255, unique=True, null=True)
	title = models.TextField(null=False, default='No title')
	gotten = models.DateTimeField(auto_now=True)
	@staticmethod
	def getsert(cl_id, url,title=None):
		item = Item.objects.filter(cl_id=cl_id).first()
		if item is None:
			item = Item(cl_id=cl_id,url=url,title=title)
			item.save()
		return item

class Hit(models.Model):
	id = models.AutoField(primary_key=True)
	search = models.ForeignKey('Search', null=True)
	item = models.ForeignKey('Item', null=True)
	@staticmethod
	def passert(item, search):
		hit = Hit.objects.filter(item=item, search=search).first()
		if hit is None:
			Hit(item=item,search=search).save()
	class Meta:
		unique_together = (('search', 'item'))

class Searcher(models.Model):
	id = models.AutoField(primary_key=True)
	email = models.CharField(max_length=255, unique=True)
	notified = models.DateTimeField(null=True, auto_now=True)
	active = models.BooleanField(default=True)
	searches = models.ManyToManyField('Search', through='Subscription')
	def all_current_items(self):
		all_items = []
		ids = []
		searches = self.searches.all()
		for search in searches:
			for item in search.items.all():
				if (datetime.now(pytz.utc) - timedelta(hours=2)) > item.gotten: continue
				item.search = search
				if item.cl_id not in ids and self.notified < item.gotten:
					all_items.append(item)
					ids.append(item.cl_id)
		return all_items
	def __str__(self):
		return self.email

class Subscription(models.Model):
	id = models.AutoField(primary_key=True)
	searcher = models.ForeignKey('Searcher', null=True)
	search = models.ForeignKey('Search', null=True)
	def __str__(self):
		return '%s >> %s' % (self.search.name, self.searcher.email)
