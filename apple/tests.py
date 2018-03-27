from django.test import TestCase

# Create your tests here.

import json
from django.core import serializers
from apple.models import *

## Test save a model to database

class ModelTestCase(TestCase):
    def setUp(self):
    	with open("test_response_data.json") as f:
    		data = json.load(f)

    def test_save_user(self):
    	result = TwitterUser.find_or_create(data['user'])
    	return self.assertEqual(14065548,result.twitter_id)


    def test_save_tweet(self):
    	result = TwitterUser.find_or_create(data)
    	return self.assertEqual(result,result.tweet_id)

    	
