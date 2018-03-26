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
		return "Twitter ID :{} screen_name: {}".format(self.twitter_id,self.screen_name)


	def create(user_response_dict):
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
		return new_user.save()



class Tweet(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(TwitterUser)

	tweet_id = models.BigIntegerField(db_index=True) # Index to make searches quicker
	text = models.CharField(max_length=250,default=None, blank=True, null=True)
	place = models.CharField(max_length=250,default=None, blank=True, null=True)
	latitude = models.DecimalField(max_digits=9, decimal_places=6)
	longitude = models.DecimalField(max_digits=9, decimal_places=6)
	retweet_count = models.BigIntegerField(default=None, blank=True, null=True)
	favourite_count = models.BigIntegerField(default=None, blank=True, null=True)

	raw_response = JSONField(default=dict)
	properties = JSONField(default=dict)

	def create(tweet_dict):
	#TODO: Abstract out to a info extractor class
		tweet_info = {'tweet_id':tweet_dict['id'],
						'text':tweet_dict['text'],
						'place':tweet_dict['place'],
						'retweet_count':tweet_dict['retweet_count'],
						'favourite_count':tweet_dict['favourite_count'],
						'raw_response':tweet_dict
						}
		coordinates = tweet_dict['coordinates']
		if coordinates:
			tweet_info['longitude'] = coordinates['coordinates'][0]
			tweet_info['latitude'] = coordinates['coordinates'][1]
		
		new_tweet = Tweet(**tweet_info)
		return new_tweet.save()

