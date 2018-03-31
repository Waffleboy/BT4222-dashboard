from apple.models import TwitterUser

def get_user_info(twitteruser_set):
	information = {}

	for user in twitteruser_set:
		username = user.screen_name
		information[username] = {}

		information[username]['twitter_id'] = user.twitter_id
		information[username]['profile_pic'] = user.profile_picture
		information[username]['followers'] = user.followers_count
		information[username]['friends'] = user.friends_count
		#information[username]['gender'] = user.gender
		#information[username]['interest'] = user.interest
		#information[username]['age'] = user.age
		information[username]['initial'] = username[0].lower()

	return information