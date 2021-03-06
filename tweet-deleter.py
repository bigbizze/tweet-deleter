import os
import time
from typing import List, Optional, NamedTuple, Callable, Union
from datetime import datetime
import twitter
import json
from TwitterType import tweet_list_from_response, dump_tweets_to_json, OneTweet


"""
DELETE_TWEETS_FOUND_IN_RANGE:
    After parsing the tweets found by your range specification, delete them if true.
    
SAVE_LAST_IDS_TO_FILE: 
    Saves a reference of the ID and datetime of the last tweet in each request,
     this is so you have reference points to begin searching from instead of 
     always starting from the most recent tweet
     
CREDENTIALS_PATH:
    Path to file containing the relevant Twitter credentials

SAVE_TWEET_DATA_PATH:
    If this contains a non-empty string, dump parsed tweets to a JSON file at this location
    
BEFORE_THIS_DATE:
    Reduce tweets list to only those found before this date
    
AFTER_THIS_DATE:
    Reduce tweets list to only those found after this date
    
START_WITH_TWEET_ID:
    Begins tweet parsing from the tweet whose ID is specified by this (instead of from the most recent tweet)
    Used in conjunction with ids found in SAVE_LAST_IDS_TO_FILE.
"""

# user defined constants
DELETE_TWEETS_FOUND_IN_RANGE = True
SAVE_LAST_IDS_TO_FILE = True

CREDENTIALS_PATH = "twitter_creds.json"
SAVE_TWEET_DATA_PATH = "deleted_tweets.json"

BEFORE_THIS_DATE = datetime(2014, 1, 1)
AFTER_THIS_DATE = None

START_WITH_TWEET_ID = 000000000000000000

# state reducer constants
API = "API"
TWEETS = "TWEETS"
EXTENDED = "EXTENDED"
RATE_CACHE = "RATE_CACHE"
RATE_CACHE_COUNT = "RATE_CACHE_COUNT"

LastTweetRef = NamedTuple(
    "LastTweetRef", (
        ("id", int),
        ("created_on", datetime)
    )
)

RateCache = NamedTuple(
    "RateCache", (
        ("time", datetime),
        ("count", int)
    )
)

Action = NamedTuple(
    "Action", (
        ("type", Union[API, TWEETS, EXTENDED, RATE_CACHE, RATE_CACHE_COUNT]),
        ("value", Optional[Union[twitter.Api, bool, List[OneTweet], datetime, int]])
    )
)

Fields = NamedTuple(
    "Fields", (
        ("api", twitter.Api),
        ("tweets", List[OneTweet]),
        ("extended", bool),
        ("rate_cache", RateCache)
    )
)

ProcessedTweets = NamedTuple(
    "ProcessedTweets", (
        ("filtered_tweets", List[OneTweet]),
        ("last_tweet_ref", LastTweetRef)
    )
)

with open(CREDENTIALS_PATH, "r") as fp:
    creds = json.load(fp)


def get_api(is_extended=False):
    return twitter.Api(consumer_key=creds["consumer_key"],
                       consumer_secret=creds["consumer_secret"],
                       access_token_key=creds["access_token_key"],
                       access_token_secret=creds["access_token_secret"],
                       tweet_mode="extended" if is_extended else None)


def field_reducer(prev_state: Optional[Fields] = None, action: Optional[Action] = None):
    return Fields(get_api(), [], False, RateCache(datetime.now(), 0)) if prev_state is None else Fields(
        api=action.value if action.type == API else prev_state.api,
        tweets=prev_state.tweets + action.value if action.type == TWEETS else prev_state.tweets,
        extended=action.value if action.type == EXTENDED else prev_state.extended,
        rate_cache=RateCache(datetime.now(), 0) if action.type == RATE_CACHE else RateCache(
            time=prev_state.rate_cache.time,
            count=action.value
        ) if action.type == RATE_CACHE_COUNT else prev_state.rate_cache
    )


def process_rate(_fields: Fields) -> Fields:
    rate_cache = _fields.rate_cache
    now = datetime.now()
    minutes_passed = (now - rate_cache.time).seconds / 60
    if not minutes_passed > 15 and not rate_cache.count > 450:
        _fields = field_reducer(_fields, Action(RATE_CACHE_COUNT, rate_cache.count + 1))
    elif minutes_passed > 15:
        _fields = field_reducer(_fields, Action(RATE_CACHE, None))
    elif rate_cache.count > 450:
        time.sleep((15 - minutes_passed) * 60)
    return _fields


def get_tweets(
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        save_last_ids: bool = True
):
    state = {"fields": field_reducer()}

    def _get_date_validation_filter() -> Callable[[List[OneTweet]], List[OneTweet]]:
        def _get_time_check_filter():
            if after is not None and before is not None:
                return lambda status: after < status.created_on_date < before
            elif after is not None:
                return lambda status: status.created_on_date > after
            elif before is not None:
                return lambda status: status.created_on_date < before
            raise RuntimeError

        def _check_valid_date(status_list: List[OneTweet]) -> List[OneTweet]:
            if after is None and before is None:
                return status_list
            return list(filter(_get_time_check_filter(), status_list))

        return _check_valid_date

    def _read_write_ids(last_tweet_ref: LastTweetRef):
        if not os.path.exists("id_store.json"):
            with open("id_store.json", "w") as _fp:
                json.dump({}, _fp)

        with open("id_store.json", "r") as _fp:
            data = json.load(_fp)

        if str(last_tweet_ref.id) in data.keys():
            return

        data[last_tweet_ref.id] = last_tweet_ref.created_on.strftime("%Y-%m-%d %H:%M:%S")
        with open("id_store.json", "w") as _fp:
            json.dump(data, _fp)

    def _get_update_tweet_state(_tweet_processor: Callable[[int], ProcessedTweets]) -> Callable[[ProcessedTweets, int], None]:
        def _check_update_tweet_state(_processed_tweets: ProcessedTweets, previous_last_id: int) -> None:
            if not state["fields"].extended and not any(_processed_tweets.filtered_tweets):
                return
            elif not state["fields"].extended and any(_processed_tweets.filtered_tweets):
                state["fields"] = field_reducer(state["fields"], Action(API, get_api(is_extended=True)))
                state["fields"] = field_reducer(state["fields"], Action(EXTENDED, True))
                processed_extended_tweets = _tweet_processor(previous_last_id)
                state["fields"] = field_reducer(state["fields"], Action(TWEETS, processed_extended_tweets.filtered_tweets))
            elif state["fields"].extended and any(_processed_tweets.filtered_tweets):
                state["fields"] = field_reducer(state["fields"], Action(TWEETS, _processed_tweets.filtered_tweets))

        return _check_update_tweet_state

    def _get_tweets_processor():
        date_filter_fn = _get_date_validation_filter()

        def _get_last_tweet_vals(status_list: List[OneTweet]) -> LastTweetRef:
            last_status = status_list[len(status_list) - 1]
            return LastTweetRef(last_status.id, last_status.created_on_date)

        def _get_tweets(_id: Optional[int] = None) -> List[OneTweet]:
            tweets_json = state["fields"].api.GetUserTimeline(creds["user_id"], max_id=_id)
            return tweet_list_from_response(json.loads(tweets_json))

        def _process_tweets(_last_id: int) -> ProcessedTweets:
            _tweets = _get_tweets(_last_id)
            _name_id_pair = _get_last_tweet_vals(_tweets)
            _filtered_tweets = date_filter_fn(_tweets)
            return ProcessedTweets(_filtered_tweets, _name_id_pair)

        return _process_tweets

    def get_tweets_(start_with_id: Optional[int] = None) -> Fields:
        tweet_processor_fn = _get_tweets_processor()
        check_update_tweet_state_fn = _get_update_tweet_state(tweet_processor_fn)
        last_id = start_with_id
        while True:
            processed_tweets = tweet_processor_fn(last_id)
            if last_id == processed_tweets.last_tweet_ref.id:
                break
            if save_last_ids:
                _read_write_ids(processed_tweets.last_tweet_ref)
            check_update_tweet_state_fn(processed_tweets, last_id)
            last_id = processed_tweets.last_tweet_ref.id
            state["fields"] = process_rate(state["fields"])
        return state["fields"]

    return get_tweets_


def delete_tweets(fields: Fields) -> None:
    state = {
        "fields": fields
    }

    api = get_api()
    for _tweet in fields.tweets:
        state["fields"] = process_rate(state["fields"])
        try:
            api.DestroyStatus(_tweet.id)
        except twitter.error.TwitterError:
            pass


def main():
    get_tweet_fn = get_tweets(after=AFTER_THIS_DATE, before=BEFORE_THIS_DATE, save_last_ids=SAVE_LAST_IDS_TO_FILE)
    fields = get_tweet_fn(start_with_id=START_WITH_TWEET_ID)

    if SAVE_TWEET_DATA_PATH:
        dump_tweets_to_json(SAVE_TWEET_DATA_PATH, fields.tweets)

    if DELETE_TWEETS_FOUND_IN_RANGE:
        delete_tweets(fields)


if __name__ == '__main__':
    main()


