from kafka import KafkaConsumer
import json
import re
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from analyse import analyse
import hashlib

from elasticsearch import Elasticsearch
#from textblob import TextBlob
es = Elasticsearch()
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5 --jars spark-streaming-kafka-0-8_2.11-2.4.5.jar --jars elasticsearch-hadoop-7.6.2.jar pyspark-shell' 
# def main():
#     '''
#     main function initiates a kafka consumer, initialize the tweetdata database.
#     Consumer consumes tweets from producer extracts features, cleanses the tweet text,
#     calculates sentiments and loads the data into postgres database
#     '''
#     # set-up a Kafka consumer
    
#     print(consumer)
#     for msg in consumer:

#         dict_data = json.loads(msg.value)
#         # tweet = TextBlob(dict_data["text"])
        
#         data = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", dict_data["text"]).split())
#         print(data)
#         print("--------------")
#         # add text and sentiment info to elasticsearch
#         # es.index(index="tweet",
#         #          doc_type="test-type",
#         #          body={"author": dict_data["user"]["screen_name"],
#         #                "date": dict_data["created_at"],
#         #                "message": dict_data["text"]})
#         print('\n')

def filter(text):
    text = re.sub(r'http\S+', "", text)
    text = ' '.join(re.sub(r'[^\w.\s#@/:%,_-]|', "", text).split())
    return text

def analys(sentence):
    return analyse(sentence)

def filtercorona(tweet):
    for i in ["#corona","#coronavirus","#covid19","#covid-19"]:
        if i in tweet:
            return True
    return False

def filterdonald(tweet):
    for i in ["#donald","#donaldtrump","#trump"]:
        if i in tweet:
            return True
    return False
    
def uploadtoelatic(data):
    es.index(index="tweet",doc_type="test-type",body={"author":"hi", "message":data})

    return

def addId(data):
    j=json.dumps(data).encode('ascii','ignore')
    data['doc_id']=hashlib.sha224(j).hexdigest()
    return (data['doc_id'],json.dumps(data))

def parse(rdd):
    d={}
    d['tweet']=rdd[0]
    d['senti']=rdd[1]
    return d


if __name__ == "__main__":
    # os.environ['PYSPARK_SUBMIT_ARGS']
    # consumer = KafkaConsumer("twitter")
    es_write_conf = {
        "es.nodes" : "localhost",
        "es.port" : "9200",
        "es.resource" : 'donaldtest/donald-doc',
        "es.input.json": "yes",
        "es.mapping.id": "doc_id"
    }

    # es_write_conf1 = {
    #     "es.nodes" : "localhost",
    #     "es.port" : "9200",
    #     "es.resource" : 'corona/corona-doc',
    #     "es.input.json": "yes",
    #     "es.mapping.id": "doc_id"
    # }
    
    conf = SparkConf().setMaster("local[*]").setAppName("twitter-app")
    sc = SparkContext(conf = conf)

    sc.setLogLevel("WARN")
    ssc = StreamingContext(sc, 10)
    ssc.checkpoint(r'./checkpoint')
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:2181', 'tweets-consumer', {"twitter":1})  
    all_data = kafkaStream.map(lambda x: json.loads(x[1]))
    sentimentanalysis = all_data.map(lambda tweet: (str(filter(tweet['text'])),analys(filter(tweet['text']))))
    forcorono=sentimentanalysis.filter(lambda x:filtercorona(x[0].lower())).map(lambda value:value).map(parse).map(addId)
    forcorono.foreachRDD(lambda rdd: rdd.saveAsNewAPIHadoopFile(
        path='-',
        outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",       
        keyClass="org.apache.hadoop.io.NullWritable",
        valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
        conf=es_write_conf1))

    # fordonald=sentimentanalysis.filter(lambda x:filterdonald(x[0].lower())).map(lambda value:value).map(parse).map(addId)
    # fordonald.foreachRDD(lambda rdd: rdd.saveAsNewAPIHadoopFile(
    #     path='-',
    #     outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",       
    #     keyClass="org.apache.hadoop.io.NullWritable",
    #     valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    #     conf=es_write_conf))
    

    ssc.start();
    ssc.awaitTermination()



