# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from datetime import timedelta
import pytz
import feedparser
# Create your models here.

class Search(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.CharField(max_length=255, unique=True)
	name = models.CharField(max_length=255, unique=True)
	items = models.ManyToManyField('Item', through='Hit')
	def __str__(self):
		return self.name
	class Meta:
		verbose_name_plural = 'Searches'
	def conduct(self):
		rss = feedparser.parse(str(self.url))
		entries = rss.entries
		for entry in entries:
			item = Item.getsert(url=str(entry.dc_source),title=str(entry.title))
			Hit.passert(item, self)

class Item(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.CharField(max_length=255, unique=True, null=True)
	title = models.TextField(null=False, default='No title')
	gotten = models.DateTimeField(auto_now=True)
	@staticmethod
	def getsert(url,title=None):
		item = Item.objects.filter(url=url).first()
		if item is None:
			item = Item(url=url,title=title)
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
		unique_together = (('search', 'item'),)

class Searcher(models.Model):
	id = models.AutoField(primary_key=True)
	email = models.CharField(max_length=255, unique=True)
	notified = models.DateTimeField(null=True, auto_now=True)
	active = models.BooleanField(default=True)
	searches = models.ManyToManyField('Search', through='Subscription')
	def all_current_items(self):
		all_items = []
		searches = self.searches.all()
		for search in searches:
			for item in search.items.all():
				if (datetime.now(pytz.utc) - timedelta(hours=2)) > item.gotten: continue
				if item.url not in all_items and self.notified < item.gotten: all_items.append(item)
		return all_items
	def __str__(self):
		return self.email

class Subscription(models.Model):
	id = models.AutoField(primary_key=True)
	searcher = models.ForeignKey('Searcher', null=True)
	search = models.ForeignKey('Search', null=True)
	def __str__(self):
		return '%s >> %s' % (self.search.name, self.searcher.email)
