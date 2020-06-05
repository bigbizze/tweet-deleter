import datetime
from typing import Optional, Any, TypeVar, Type, cast, List, Callable

T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_dict(x: Any) -> dict:
    assert isinstance(x, dict)
    return x


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class User:
    screen_name: Optional[str]
    name: Optional[str]
    id: Optional[int]
    indices: Optional[List[int]]

    def __init__(self, screen_name: Optional[str], name: Optional[str], id: Optional[int], indices: Optional[List[int]]) -> None:
        self.screen_name = screen_name
        self.name = name
        self.id = id
        self.indices = indices

    @staticmethod
    def from_dict(obj: Any) -> 'User':
        assert isinstance(obj, dict)
        screen_name = from_union([from_str, from_none], obj.get("screen_name"))
        name = from_union([from_str, from_none], obj.get("name"))
        id = from_union([from_int, from_none], obj.get("id"))
        indices = from_union([lambda x: from_list(from_int, x), from_none], obj.get("indices"))
        return User(screen_name, name, id, indices)

    def to_dict(self) -> dict:
        return {
            "screen_name": from_union([from_str, from_none], self.screen_name),
            "name": from_union([from_str, from_none], self.name),
            "id": from_union([from_int, from_none], self.id),
            "indices": from_union([lambda x: from_list(from_int, x), from_none], self.indices)
        }


class TweetMetaInfo:
    is_quote_status: Optional[bool]
    retweet_count: Optional[int]
    favorite_count: Optional[int]
    favorited: Optional[bool]
    retweeted: Optional[bool]
    possibly_sensitive: Optional[bool]
    lang: Optional[str]
    in_reply_to_status_id: Optional[int]
    in_reply_to_user_id: Optional[int]
    in_reply_to_screen_name: Optional[str]

    def __init__(self, is_quote_status: Optional[bool], retweet_count: Optional[int], favorite_count: Optional[int], favorited: Optional[bool], retweeted: Optional[bool], possibly_sensitive: Optional[bool], lang: Optional[str], in_reply_to_status_id: Optional[int], in_reply_to_user_id: Optional[int], in_reply_to_screen_name: Optional[str]) -> None:
        self.is_quote_status = is_quote_status
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.favorited = favorited
        self.retweeted = retweeted
        self.possibly_sensitive = possibly_sensitive
        self.lang = lang
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_user_id = in_reply_to_user_id
        self.in_reply_to_screen_name = in_reply_to_screen_name

    @staticmethod
    def from_dict(obj: Any) -> 'TweetMetaInfo':
        assert isinstance(obj, dict)
        is_quote_status = from_union([from_bool, from_none], obj.get("is_quote_status"))
        retweet_count = from_union([from_int, from_none], obj.get("retweet_count"))
        favorite_count = from_union([from_int, from_none], obj.get("favorite_count"))
        favorited = from_union([from_bool, from_none], obj.get("favorited"))
        retweeted = from_union([from_bool, from_none], obj.get("retweeted"))
        possibly_sensitive = from_union([from_bool, from_none], obj.get("possibly_sensitive"))
        lang = from_union([from_str, from_none], obj.get("lang"))
        in_reply_to_status_id = from_union([from_int, from_none], obj.get("in_reply_to_status_id"))
        in_reply_to_user_id = from_union([from_int, from_none], obj.get("in_reply_to_user_id"))
        in_reply_to_screen_name = from_union([from_str, from_none], obj.get("in_reply_to_screen_name"))
        return TweetMetaInfo(is_quote_status, retweet_count, favorite_count, favorited, retweeted, possibly_sensitive, lang, in_reply_to_status_id, in_reply_to_user_id, in_reply_to_screen_name)

    def to_dict(self) -> dict:
        return {
            "is_quote_status": from_union([from_bool, from_none], self.is_quote_status),
            "retweet_count": from_union([from_int, from_none], self.retweet_count),
            "favorite_count": from_union([from_int, from_none], self.favorite_count),
            "favorited": from_union([from_bool, from_none], self.favorited),
            "retweeted": from_union([from_bool, from_none], self.retweeted),
            "possibly_sensitive": from_union([from_bool, from_none], self.possibly_sensitive),
            "lang": from_union([from_str, from_none], self.lang),
            "in_reply_to_status_id": from_union([from_int, from_none], self.in_reply_to_status_id),
            "in_reply_to_user_id": from_union([from_int, from_none], self.in_reply_to_user_id),
            "in_reply_to_screen_name": from_union([from_str, from_none], self.in_reply_to_screen_name)
        }


class OneTweet:
    created_at: Optional[str]
    id: Optional[int]
    id_str: Optional[str]
    full_text: Optional[str]
    text: Optional[str]
    created_on_date: Optional[datetime.datetime]
    users: Optional[List['User']]
    meta_info: Optional[TweetMetaInfo]

    def __init__(self, created_at: Optional[str], id_str: Optional[str], full_text: Optional[str], text: Optional[str], users: Optional[List['User']], meta_info: TweetMetaInfo) -> None:
        self.created_at = created_at
        self.id_str = id_str
        self.full_text = full_text
        self.text = text
        self.users = users
        self.id = int(self.id_str) if isinstance(self.id_str, str) else None
        self.created_on_date = self.get_created_on_date()
        self.meta_info = meta_info

    def get_created_on_date(self):
        created_at_ls = self.created_at.split("+")
        if not created_at_ls or not len(created_at_ls) == 2:
            return None
        year_ls = created_at_ls[1].split(" ")
        if not year_ls or not len(year_ls) == 2:
            return None
        created_at = f"{created_at_ls[0].strip()} {year_ls[1].strip()}"
        return datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S %Y")

    @staticmethod
    def from_dict(obj: Any) -> 'OneTweet':
        assert isinstance(obj, dict)
        created_at = from_union([from_str, from_none], obj.get("created_at"))
        id_str = from_union([from_str, from_none], obj.get("id_str"))
        full_text = from_union([from_str, from_none], obj.get("full_text"))
        text = from_union([from_str, from_none], obj.get("text"))
        user = [from_union([User.from_dict, from_none], x) for x in from_union([from_dict, from_none], obj.get("entities")).get("user_mentions")]
        meta_info = from_union([TweetMetaInfo.from_dict, from_none], obj)
        return OneTweet(created_at, id_str, full_text, text, user, meta_info)

    def to_dict(self) -> dict:
        return {
            "created_at": from_union([from_str, from_none], self.created_at),
            "id_str": from_union([from_str, from_none], self.id_str),
            "full_text": from_union([from_str, from_none], self.full_text),
            "text": from_union([from_str, from_none], self.text),
            "users": from_union([lambda x: from_list(lambda _x: to_class(User, _x), x), from_none], self.users),
            "meta_info": from_union([lambda x: x.to_dict(), from_none], self.meta_info)
        }


class TwitterType:
    @staticmethod
    def from_response(raw_tweets: List[any]) -> List['OneTweet']:
        assert isinstance(raw_tweets, list)
        return [OneTweet.from_dict(x) for x in raw_tweets]

    @staticmethod
    def to_dict(tweet_list: List[OneTweet]) -> dict:
        return {
            "tweets": [to_class(OneTweet, tweet) for tweet in tweet_list]
        }

    @staticmethod
    def to_json(tweet_list: List[OneTweet], fn: str) -> None:
        import json
        with open(fn, "w") as fp:
            json.dump(TwitterType.to_dict(tweet_list), fp)


def one_tweet_from_dict(s: Any) -> List['OneTweet']:
    return TwitterType.from_response(s)


def welcome_to_dict(x: TwitterType) -> Any:
    return to_class(TwitterType, x)
