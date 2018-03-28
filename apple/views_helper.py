

def format_tweets_to_table(tweet_query_set):
	return [[x.created_at.strftime("%d/%m /%Y %M:%S"),x.user.screen_name,x.text,'LOW'] for x in tweet_query_set]
	
def format_other_tweets_to_table(tweet_query_set):
	return [[x.created_at.strftime("%d/%m /%Y %M:%S"),x.user.screen_name,x.text] for x in tweet_query_set]
	