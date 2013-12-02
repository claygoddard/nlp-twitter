import twitter
import nltk
from collections import defaultdict
import twokenize
import operator
import keys

class TweetStats():
    def __init__(self, statuses):
        self.word_counts = defaultdict(int)
        self.bigram_counts = defaultdict(lambda: defaultdict(int))
        statuses_processed = [twokenize.tokenize(s.text) for s in statuses]
        self.process_word_counts(statuses_processed)
        self.process_bigram_counts(statuses_processed)
        
    def process_word_counts(self, statuses):
        for status in statuses:
            for word in status:
                self.word_counts[word] += 1
    
    def process_bigram_counts(self, statuses):
        for status in statuses:
            for i in xrange(1, len(status)):
                self.bigram_counts[status[i-1]][status[i]] += 1
    
    def sorted_word_counts(self):
        return sorted(self.word_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    def sorted_bigram_counts(self):
        flattened = defaultdict(int)
        for first_word, dict in self.bigram_counts.iteritems():
            for second_word, count in dict.iteritems():
                flattened["(" + first_word + ", " + second_word + ")"] = count
        return sorted(flattened.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    def __str__(self):
        ret_s = "===STATS===\n"
        ret_s += "top 30 word counts:\n"
        ret_s += "\n".join([item[0] + " : " + str(item[1]) for item in self.sorted_word_counts()[:30]]) + "\n"
        ret_s += "top 30 bigram counts:\n"
        ret_s += "\n".join([item[0] + " : " + str(item[1]) for item in self.sorted_bigram_counts()[:30]]) + "\n"
        ret_s += "===END===\n"
        return ret_s
        

def run():
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
    user_statuses = api.GetUserTimeline(user_id=user.id, count=3200, include_rts=False)
    #hashtag_statuses = api.GetSearch(term=hashtag, count=3200)
    
    user_stats = TweetStats(user_statuses)
    #hashtag_stats = TweetStats(hashtag_statuses)
    
    print user_stats
    
    
if __name__ == "__main__":
    run()
