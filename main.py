import twitter
import nltk
from collections import defaultdict
import twokenize
import operator
import keys
import codecs
import sys
import shelve

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
        ret_s.encode('utf-8')
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
        
    user_statuses_shelve = shelve.open('user_statuses')
    hashtag_statuses_shelve = shelve.open('hashtag_statuses')
    
    print user_statuses_shelve.keys()
    
    user_statuses_shelve_data = user_statuses_shelve.get('data', None)
    hashtag_statuses_shelve_data = hashtag_statuses_shelve.get('data', None)
    
    user_statuses = user_statuses_shelve_data
    if user_statuses is None:
        print "Grabbing user statuses"
        user = api.GetUser(screen_name=username)
        user_statuses = api.GetUserTimeline(user_id=user.id, count=200, include_rts=False)
        user_statuses_shelve['data'] = user_statuses
    
    hashtag_statuses = hashtag_statuses_shelve_data
    if hashtag_statuses is None:
        print "Grabbing hashtag statuses"
        hashtag_statuses = api.GetSearch(term=hashtag, count=100)
        min_id = min([item.id for item in hashtag_statuses])
        for i in xrange(5):
            more = api.GetSearch(term=hashtag, count=100, max_id=min_id)
            min_id = min([item.id for item in more])
            hashtag_statuses.extend(more)
        hashtag_statuses_shelve['data'] = hashtag_statuses
    
    user_statuses_shelve.close()
    hashtag_statuses_shelve.close()
    
    user_stats = TweetStats(user_statuses)
    hashtag_stats = TweetStats(hashtag_statuses)
    
    out = codecs.getwriter('utf-8')(sys.stdout)
    out.write(user_stats.__str__())
    out.write("\n\n\n")
    out.write(hashtag_stats.__str__())
    
    
if __name__ == "__main__":
    run()
