import time
import snscrape.modules.twitter as sntwitter
import datetime
from datetime import timedelta
import pymongo
import threading
import pytz

# client = pymongo.MongoClient('mongodb://localhost:27017')
# db = client['twitter_data']
# tracker_collection = db.twitter_realtime_tracker
# detail_data = db.twitter_realtime_data

client = pymongo.MongoClient('mongodb+srv://alphaTrendDbUser:tj7NkzXcE0v4D7T6@alphatrend.vrkhi.mongodb.net/test')
db = client['alpha-trend-db']

tracker_collection = db.twitter_tracker
detail_data = db.twitter_detail

def start_symbol(symbol):
    time_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    end_date = str((datetime.datetime.utcnow() + timedelta(hours=24)).date())
    start_date = str((datetime.datetime.utcnow() - timedelta(hours=24)).date())

    print(f"scraping for {symbol}")
    tweets = sntwitter.TwitterSearchScraper(
                    f"${symbol} until:{end_date} since:{start_date}").get_items()
    
    tmp = []
    for tweet in tweets:
        if tweet.date < (time_now - timedelta(minutes=15)):
            break
        tweet_info = {
                    'id': tweet.id,
                    'link': tweet.url,
                    'symbol': symbol,
                    'username': tweet.user.username,
                    'user_id': tweet.user.id,
                    'tweet': tweet.rawContent,
                    'retweet_count': tweet.retweetCount,
                    'likes': tweet.likeCount,
                    'reply_count': tweet.replyCount,
                    'post_time': tweet.date,
                    'views': tweet.viewCount if tweet.viewCount else 0,
                    'followers': tweet.user.followersCount,
                    'user_verified': tweet.user.verified,
                    'quote_count': tweet.quoteCount,
                    
                }
        tmp.append(tweet_info)
    if len(tmp) > 0:
        detail_data.insert_many(tmp)

symbols = tracker_collection.distinct("symbol")

def main():


    # symbols = tracker_collection.distinct("symbol")#['$TSLA','$AAPL','$ABBV','$AID','$ANT']
    symbols_all = tracker_collection.distinct("symbol")
    # symbols = [symbol for symbol in symbols_all if symbol not in ['TSLA']]
    symbols = [symbol for symbol in symbols_all if symbol not in ['TSLA', 'AAPL', 'AMZN', 'FB', 'GOOG', 'MSFT', 'NVDA']]
    thread_count = len(symbols)
    #thread_count = 3


    threads = []
    tickers_count = thread_count if thread_count > 0 else len(symbols)
    print(f"Starting threads total {thread_count} threads for {','.join(symbols[:tickers_count])} tickers")
    time.sleep(5)
    for symbol in symbols[:tickers_count]:
        t = threading.Thread(target=start_symbol, args=(symbol,))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


main()
