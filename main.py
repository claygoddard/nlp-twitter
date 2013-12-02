import twitter
import nltk
from collections import defaultdict
import twokenize
import operator
import keys

api = twitter.Api(
    consumer_key = keys.CONSUMER_KEY,
    consumer_secret = keys.CONSUMER_SECRET,
    access_token_key = keys.ACCESS_TOKEN_KEY,
    access_token_secret = keys.ACCESS_TOKEN_SECRET
)

username = "CrisGoddard"#raw_input("Twitter username: ")
hashtag = "obama"#raw_input("Twitter hashtag: ")

if hashtag[0] != "#":
    hashtag = "#" + hashtag

user = api.GetUser(screen_name=username)
statuses = api.GetUserTimeline(user_id=user.id, count=200, include_rts=False)

word_count = defaultdict(int)

for s in statuses:
    words = twokenize.tokenize(s.text)
    for word in words:
        word_count[word] += 1

print sorted(word_count.iteritems(), key=operator.itemgetter(1), reverse=True)[:15]
