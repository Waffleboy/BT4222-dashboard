from django.db import models
from django.contrib.postgres.fields import JSONField
import pandas as pd
import datetime
from collections import Counter,defaultdict

import logging
logger = logging.getLogger(__name__)

# Create your models here.

class TwitterUser(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	twitter_id = models.BigIntegerField(db_index=True) # Index to make searches quicker
	screen_name = models.CharField(max_length=100,default=None, blank=True, null=True)
	name = models.CharField(max_length=100,default=None, blank=True, null=True)
	profile_picture = models.CharField(max_length=250,default=None, blank=True, null=True)
	location = models.CharField(max_length=250,default=None, blank=True, null=True)
	description = models.CharField(max_length=250,default=None, blank=True, null=True)
	time_zone = models.CharField(max_length=100,default=None, blank=True, null=True)
	followers_count = models.BigIntegerField(default=None, blank=True, null=True)
	friends_count = models.BigIntegerField(default=None, blank=True, null=True)
	url = models.CharField(max_length=250,default=None, blank=True, null=True)


	raw_response = JSONField(default=dict)
	properties = JSONField(default=dict)

	def __str__(self):
		return "Twitter ID: {} screen_name: {}".format(self.twitter_id,self.screen_name)


	def find_or_create(user_response_dict):
		query = TwitterUser.objects.filter(twitter_id=user_response_dict['id'])
		if len(query) > 0:
			return query.first()

		#TODO: Abstract out to a info extractor class
		user_info = {'twitter_id': user_response_dict['id'],
					  'screen_name':user_response_dict['screen_name'],
					  'name':user_response_dict['name'],
					  'profile_picture':user_response_dict['profile_image_url_https'],
					 'location':user_response_dict['location'],
					 'description':user_response_dict['description'],
					 'time_zone':user_response_dict['time_zone'],
					 'followers_count':user_response_dict['followers_count'],
					 'friends_count':user_response_dict['friends_count'],
					 'url':user_response_dict['url'],
					 'raw_response':user_response_dict
					 }

		new_user = TwitterUser(**user_info)
		new_user.save()
		return new_user
		



class Tweet(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(TwitterUser)

	tweet_id = models.BigIntegerField(db_index=True) # Index to make searches quicker
	text = models.CharField(max_length=250,default=None, blank=True, null=True)
	place = models.CharField(max_length=250,default=None, blank=True, null=True)
	latitude = models.DecimalField(max_digits=9, decimal_places=6,default=None, blank=True, null=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6,default=None, blank=True, null=True)
	retweet_count = models.BigIntegerField(default=None, blank=True, null=True)
	favorite_count = models.BigIntegerField(default=None, blank=True, null=True)

	raw_response = JSONField(default=dict)
	properties = JSONField(default=dict)

	def __str__(self):
		return "Tweet ID: {}".format(self.tweet_id)


	def find_or_create(tweet_dict):
		query = Tweet.objects.filter(tweet_id=tweet_dict['id'])
		if len(query) > 0:
			return query.first()

		#TODO: Abstract out to a info extractor class
		tweet_info = {'tweet_id':tweet_dict['id'],
						'text':tweet_dict['text'],
						'place':tweet_dict['place'],
						'retweet_count':tweet_dict['retweet_count'],
						'favorite_count':tweet_dict['favorite_count'],
						'raw_response':tweet_dict
						}

		coordinates = tweet_dict['coordinates']
		if coordinates:
			tweet_info['longitude'] = coordinates['coordinates'][0]
			tweet_info['latitude'] = coordinates['coordinates'][1]
		
		user_id = tweet_dict['user']['id']
		user = TwitterUser.find_or_create(tweet_dict['user'])
		tweet_info['user'] = user

		new_tweet = Tweet(**tweet_info)
		new_tweet.save()
		return new_tweet

