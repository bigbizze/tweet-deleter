# tweet-deleter

Basic functional wrapper around the python-twitter library that allows you to select a range of tweets between two dates, parse them into the data I arbitrarily considered to be useful (I feel like I'm a good judge of this, but you can check TwitterType.py to see the fields included), and optionally dumps this to a JSON file prior to optionally deleteing them from your Twitter account.

Enter the appropriate Api application credentials into "twitter_creds.json" & change the flags at the top of tweet-deleter.py to the settings you'd like.

I wrote this in only a few hours so I would definitely recommend running it once with the "DELETE_TWEETS_FOUND_IN_RANGE" flag set to false, and a path provided to "SAVE_TWEET_DATA_PATH" so you can have a look at the tweets it has found for deletion.

Use at your own risk (it worked fine for me for what that's worth).
