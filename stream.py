from kafka import KafkaProducer
import kafka
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import re


# TWITTER API CONFIGURATIONS
consumer_key = "jlHmf3kOTKTbr0k7S0hYAAIFk"
consumer_secret = "vUdtAruIWL4IsxALrwUW59fJLg2pxSDqnZ3zH8m7yVjkUxLRx5"
access_token = "873723202467319808-vratbHA3hSi5WKSi4UHTwNL1qbR7pLM"
access_secret = "RaXxven5WBrxB6sZWuHU1waZdRI7HHgg3elok7Mh3W2zv"

# TWITTER API AUTH
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

 
# Twitter Stream Listener
class KafkaPushListener(StreamListener):
    def __init__(self):
        # localhost:9092 = Default Zookeeper Producer Host and Port Adresses
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    # Get Producer that has topic name is Twitter
    # self.producer = self.client.topics[bytes("twitter")].get_producer()

    def on_data(self, data):
        # Producer produces data for consumer
        # Data comes from Twitter
        # text=data["text"]
        # json_data=(json.loads(data))
        # text=json.dumps(json_data["text"])
        # text = re.sub(r'http\S+', "", text)
        # text = ' '.join(re.sub(r'[^\w.\s#@/:%,_-]|', "", text).split())
        # # print(text)       
        # tweetid=json.dumps(json_data["id_str"])
        # text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())
        print(data)
        self.producer.send("twitter", data.encode('utf-8'))
        print("---------------------------")

        return True

    def on_error(self, status):
        print(status)
        return True


# Twitter Stream Config
twitter_stream = Stream(auth, KafkaPushListener())

# Produce Data that has trump hashtag (Tweets)
twitter_stream.filter(track=['#trump','#coronavirus'])