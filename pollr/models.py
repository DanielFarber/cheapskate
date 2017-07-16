# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
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
			item = Item.getsert(str(entry.dc_source))
			Hit.passert(item, self)

class Item(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.CharField(max_length=255, unique=True, null=True)
	gotten = models.DateTimeField(auto_now=True)
	@staticmethod
	def getsert(url):
		item = Item.objects.filter(url=url).first()
		if item is None:
			item = Item(url=url)
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
