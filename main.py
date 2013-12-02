import twitter
import nltk
from collections import defaultdict
import twokenize
import operator
import keys
import codecs
import sys
import shelve
import math

class TweetStats():
    def __init__(self, statuses, alpha=.001):
        self.alpha = alpha
        self.total_words = 0
        self.word_counts = defaultdict(int)
        self.total_word_counts = 0
        self.bigram_counts = defaultdict(lambda: defaultdict(int))
        self.total_bigram_counts = defaultdict(int)
        self.starting_word_counts = defaultdict(int)
        self.total_starting_word_counts = 0
        statuses_processed = [twokenize.tokenize(s.text.lower()) for s in statuses]
        self.process_total_words(statuses_processed)
        self.process_word_counts(statuses_processed)
        self.process_bigram_counts(statuses_processed)
        self.process_starting_word_counts(statuses_processed)
        
    def process_total_words(self, statuses):
        self.total_words = 0
        for status in statuses:
            self.total_words += len(status)
        
    def process_word_counts(self, statuses):
        for status in statuses:
            for word in status:
                self.word_counts[word] += 1
                self.total_word_counts += 1
    
    def process_bigram_counts(self, statuses):
        for status in statuses:
            for i in xrange(1, len(status)):
                self.bigram_counts[status[i-1]][status[i]] += 1
                self.total_bigram_counts[status[i-1]] += 1
    
    def process_starting_word_counts(self, statuses):
        for status in statuses:
            self.starting_word_counts[status[0]] += 1
            self.total_starting_word_counts += 1
            
    def log_prob_word(self, word):
        return math.log(self.word_counts[word] + self.alpha * self.total_word_counts) - math.log(self.total_word_counts + self.alpha)
    
    def log_prob_bigram(self, first_word, second_word):
        return math.log(self.bigram_counts[first_word][second_word] + self.alpha * self.total_bigram_counts[first_word]) - math.log(self.total_bigram_counts[first_word] + self.alpha)
    
    def log_prob_starting_word(self, word):
        return math.log(self.starting_word_counts[word] + self.alpha * self.total_starting_word_counts) - math.log(self.total_starting_word_counts)
    
    def sorted_word_counts(self):
        return sorted(self.word_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    def sorted_bigram_counts(self):
        flattened = defaultdict(int)
        for first_word, dict in self.bigram_counts.iteritems():
            for second_word, count in dict.iteritems():
                flattened["(" + first_word + ", " + second_word + ")"] = count
        return sorted(flattened.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    def sorted_starting_word_counts(self):
        return sorted(self.starting_word_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    def __str__(self):
        ret_s = "===STATS===\n"
        ret_s += "top 30 word counts:\n"
        ret_s += "\n".join([item[0] + " : " + str(item[1]) for item in self.sorted_word_counts()[:30]]) + "\n\n"
        ret_s += "top 30 bigram counts:\n"
        ret_s += "\n".join([item[0] + " : " + str(item[1]) for item in self.sorted_bigram_counts()[:30]]) + "\n\n"
        ret_s += "top 30 starting word counts:\n"
        ret_s += "\n".join([item[0] + " : " + str(item[1]) for item in self.sorted_word_counts()[:30]]) + "\n"
        ret_s += "===END===\n"
        ret_s.encode('utf-8')
        return ret_s

def best_starting_word(user_stats, hashtag_stats):
    best_prob = None
    best_word = None
    for word in hashtag_stats.starting_word_counts.keys():
        prob = user_stats.log_prob_starting_word(word) + hashtag_stats.log_prob_starting_word(word)
        if best_prob is None or prob > best_prob:
            best_prob = prob
            best_word = word
    return best_word

def run():
    api = None # initialized later if needed
    
    username = "CrisGoddard"#raw_input("Twitter username: ")
    hashtag = "obama"#raw_input("Twitter hashtag: ")
    
    if hashtag[0] != "#":
        hashtag = "#" + hashtag
        
    user_statuses_shelve = shelve.open('user_statuses')
    hashtag_statuses_shelve = shelve.open('hashtag_statuses')
    
    if 'data' in user_statuses_shelve.keys():
        print 'User statuses data exists'
    
    if 'data' in hashtag_statuses_shelve.keys():
        print 'Hashtag statuses data exists'
    
    user_statuses_shelve_data = user_statuses_shelve.get('data', None)
    hashtag_statuses_shelve_data = hashtag_statuses_shelve.get('data', None)
    
    if user_statuses_shelve_data is None or hashtag_statuses_shelve_data is None:
        api = twitter.Api(
                          consumer_key = keys.CONSUMER_KEY,
                          consumer_secret = keys.CONSUMER_SECRET,
                          access_token_key = keys.ACCESS_TOKEN_KEY,
                          access_token_secret = keys.ACCESS_TOKEN_SECRET
                          )
    
    user_statuses = user_statuses_shelve_data
    if user_statuses is None:
        print "Grabbing user statuses"
        user = api.GetUser(screen_name=username)
        user_statuses = api.GetUserTimeline(user_id=user.id, count=200, include_rts=False)
        user_statuses_shelve['data'] = user_statuses
    
    hashtag_statuses = hashtag_statuses_shelve_data
    if hashtag_statuses is None:
        print "Grabbing hashtag statuses"
        query = hashtag + " -RT"
        hashtag_statuses = api.GetSearch(term=query, result_type='mixed', count=100)
        min_id = min([item.id for item in hashtag_statuses])
        for i in xrange(10):
            more = api.GetSearch(term=query, result_type='mixed', count=100, max_id=min_id)
            min_id = min([item.id for item in more])
            hashtag_statuses.extend(more)
        hashtag_statuses_shelve['data'] = hashtag_statuses
    
    user_statuses_shelve.close()
    hashtag_statuses_shelve.close()
    
    user_stats = TweetStats(user_statuses)
    hashtag_stats = TweetStats(hashtag_statuses)
    
    """out = codecs.getwriter('utf-8')(sys.stdout)
    out.write(user_stats.__str__())
    out.write("\n\n\n")
    out.write(hashtag_stats.__str__())"""
    print best_starting_word(user_stats, hashtag_stats)
    
    
if __name__ == "__main__":
    run()
