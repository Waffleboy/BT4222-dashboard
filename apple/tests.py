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
    	return self.assertEqual(result,True)


    def test_save_tweet(self):
    	tweet = objs[0]

    	return self.assertEqual(result,True)

    	
