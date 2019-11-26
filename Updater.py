# Import libraries
# Twitter 
import tweepy
from tweepy import OAuthHandler

# Classification
import pandas as pd
import numpy as np
import string
import nltk
import sklearn
import matplotlib
import matplotlib.pyplot as plt 
from sklearn.externals import joblib

# Requests for Solr and multithreading
import requests
from multiprocessing.dummy import Pool as ThreadPool 

# Misc 
import time
import json
import datetime

# Setup Twitter authentications
dt = datetime.datetime.now()
auth, api, all_tweets, results = None, None, [], []
filename = str(dt.year)+"-"+str(dt.month)+"-"+str(dt.day) + \
		"-"+str(dt.hour)+"-"+str(dt.minute)+"-"+str(dt.second)

accounts = [ {'name': 'BBCSport', 'latestID': ''}, 
			{'name': 'verge', 'latestID': ''}, 
			{'name': 'TheEconomist', 'latestID': ''}, 
			{'name': 'CNN', 'latestID': ''}, 
			{'name': 'WSJ', 'latestID': ''}
		   ]

updateLimit = 200 # Fetch a maximum of X tweets from each handler for update

loaded_model = joblib.load('./Data/saved_model.sav')


def setupTwitter():
	global auth
	global api
	# Setup auth keys
	consumer_key = "XX"
	consumer_secret = "XX"
	access_key = "YY"
	access_secret = "YY"
	
	# Setup authentication
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

# Setup Solr requests
def setLatestID():
	global accounts
	for acc in accounts:
		r = requests.get('http://localhost:8983/solr/ir/select?df=tweet_text&fq=screen_name%3A'+acc['name']+'&q=*%3A*&sort=id%20desc')
		response = r.json()
		latestID = response['response']['docs'][0]['id']
		acc['latestID'] = latestID

 # Setup Twitter requests
def fetch(acc):
	global all_tweets
	noOfTweetsFetched = 0
	
	i_array = []
	latest = acc['latestID']
	new_tweets = api.user_timeline(screen_name='@'+acc['name'], count=200, since_id=latest, tweet_mode='extended')
	if(len(new_tweets) > 0):
		i_array.extend(new_tweets)
		A = new_tweets[0].id # Later tweet
		B = new_tweets[-1].id # Earlier tweet
		noOfTweetsFetched += len(new_tweets)
	
		if(len(new_tweets) == 200):
			while(int(new_tweets[-1].id) > int(latest) and len(i_array)<updateLimit):
				new_tweets = api.user_timeline(screen_name='@'+acc['name'], count=200, max_id=B, tweet_mode='extended')
				if(len(new_tweets) > 0):
					i_array.extend(new_tweets)
					B = new_tweets[-1].id
					noOfTweetsFetched += len(new_tweets)
				else:
					break
	print("\t[{}] Fetched {} new tweets since ID: {}".format(
		acc['name'], str(noOfTweetsFetched), acc['latestID']))
	all_tweets.extend(i_array)

def fetchTweets():
	# We are limited to 1500 requests / min. For demonstration, we shall fetch 200 tweets since the latest one cached in Solr
	# By using threading, we reduced the time taking for fetching of tweets from 18 seconds to 3 seconds
	global all_tweets

	setupTwitter()
	pool = ThreadPool(5)
	start = time.time()
	results = pool.map(fetch, accounts)
	end = time.time()
	pool.close()
	pool.join()
	print("Elapsed time: {}".format(end - start))


# Parse and save results
def saveResults():
	global results
	for a in all_tweets:
		results.append(a._json)
		
	# Save raw json to file
	with open('./Data/Json/'+filename+'.json', 'w') as outfile:
		json.dump(results, outfile)

def extractInformation():
	arr = []
	for t in results:
		new_dict = {'username': t["user"]["name"],
					'profile_image_url': t["user"]["profile_image_url"],
					'screen_name': t["user"]["screen_name"],
					'profile_description': t["user"]["description"],
					'tweet_id': t["id_str"],
					'tweet_creation': t["created_at"],
					'tweet_text': t["full_text"],
					'tweet_fav_count': t["favorite_count"],
					'tweet_retweet_count': t["retweet_count"]}
		# Check if there's any media
		if("entities" in t):
			if('media' in t["entities"]):
				# print("HAVE MEDIA")
				new_dict["tweet_media_url"] = t["entities"]["media"][0]["media_url"]
			else:
				# print("NO MEDIA")
				new_dict["tweet_media_url"] = ""
		else:
			# print(">> not exist")
			new_dict["tweet_media_url"] = ""
		arr.append(new_dict)
	return arr

def getDataframe(arr):
	pd.set_option('display.float_format', lambda x: '%.3f' % x)
	df = pd.DataFrame.from_dict(arr)
	df['tweet_id'] = pd.to_numeric(df["tweet_id"])
	return df

def saveToCSV(df):
	df.to_csv('./Data/CSV/'+filename+'.csv', encoding='utf-16',  float_format='%19f', index=False)

# Classification
from nltk.stem.porter import *


def remove_pattern(input_txt, pattern):
	r = re.findall(pattern, input_txt)
	for i in r:
		input_txt = re.sub(i, '', input_txt)
	return input_txt


def remove_link(input_txt, pattern):
	r = re.findall(pattern, input_txt)
	for i in r:
		input_txt = re.sub(i, '', input_txt)
	return input_txt

def preprocess(df):
	# remove twitter handles
	df['tidy_tweet'] = np.vectorize(remove_pattern)(df['tweet_text'], "@[\w]*")

	# remove links
	df['tidy_tweet'] = np.vectorize(remove_link)(df['tidy_tweet'], "http\S+")

	# remove special characters and numbers
	df['tidy_tweet'] = df['tidy_tweet'].str.replace("[^a-zA-Z]", " ")

	# remove word with less than 3 characters
	df['tidy_tweet'] = df['tidy_tweet'].apply(
		lambda x: ' '.join([w for w in x.split() if len(w) > 3]))

	tokenized_tweet = df['tidy_tweet'].apply(lambda x: x.split())
	tokenized_tweet.head()

	stemmer = PorterStemmer()

	tokenized_tweet = tokenized_tweet.apply(
		lambda x: [stemmer.stem(i) for i in x])  # stemming
	tokenized_tweet.head()

	for i in range(len(tokenized_tweet)):
		tokenized_tweet[i] = ' '.join(tokenized_tweet[i])

	df['tidy_tweet'] = tokenized_tweet
	df.tidy_tweet

	return df

def predict(df):
	new_df = preprocess(df)
	X_new = new_df.tidy_tweet
	y_new = loaded_model.predict(X_new)

	category = []

	for i in range(len(X_new)):
		# print("X=%s" % (X_new[i]))
		# print("Predicted=%s" %  y_new[i])
		category.append(y_new[i])

	new_df.insert(10, "category", category, True)
	new_df.head(5)
	
	plt.figure(figsize=(10, 4))
	new_df.category.value_counts().plot(kind='bar')
	return new_df

# Convert XML to Solr
def convertToXML(df):
	i = 0
	def iso(t):
		st = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(t,'%a %b %d %H:%M:%S +0000 %Y'))
		return st
	xml = "<add>\n"
	for index, row in df.iterrows():
		xml += '<doc>\n'
		xml += '  <field name="id">{}</field>\n'.format(row['tweet_id'])
		xml += '  <field name="tweet_text">{}</field>\n'.format(row['tweet_text'].replace('&', '&amp;'))
		xml += '  <field name="username">{}</field>\n'.format(row['username'])
		xml += '  <field name="tweet_retweet_count">{}</field>\n'.format(row['tweet_retweet_count'])
		xml += '  <field name="tweet_media_url">{}</field>\n'.format(row['tweet_media_url'])
		xml += '  <field name="tweet_fav_count">{}</field>\n'.format(row['tweet_fav_count'])
		xml += '  <field name="screen_name">{}</field>\n'.format(row['screen_name'])
		xml += '  <field name="profile_image_url">{}</field>\n'.format(row['profile_image_url'])
		xml += '  <field name="profile_description">{}</field>\n'.format(row['profile_description'].replace('&', '&amp;'))
		xml += '  <field name="tweet_creation">{}</field>\n'.format(iso(row['tweet_creation']))
		xml += '  <field name="category">{}</field>\n'.format(row['category'])
		xml += '</doc>\n'
		i+=1
	xml += '</add>'
	print(">>> "+str(i))
	return xml

def saveXML(xml):
	f = open('./Data/XML/'+filename+'.xml', 'w', encoding='utf-8')
	f.write(xml)

# Push XML to Solr
def pushSolr(xml):
	import xml.etree.ElementTree as ET
	
	url = 'http://localhost:8983/solr/ir/update?commit=true'
	headers = {'content-type': 'text/xml'}
	payload = xml.encode('utf-8')
	r = requests.post(url, data=payload, headers=headers)
	responseXml = ET.fromstring(r.text)

	for x in responseXml.findall('lst/int'):
		if(x.get('name') == 'status'):
			if(x.text == '0'):
				print("[+] Posted to Solr!")
			else:
				print("\033[91m [-] Error with posting to Solr")
				print(r.text)


def update():
	# Reset
	global all_tweets
	global results
	all_tweets, results = [], []
	# Get latest IDs
	setLatestID()
	print("[+] Fetched latest IDs ")

	# Fetch tweets
	fetchTweets()
	print(len(all_tweets))
	print("[+] Retrieved tweets ")
	if(len(all_tweets) > 0):
		# Save tweets as raw JSON
		saveResults()
		print("[+] Saved tweets as raw JSON - {}".format(len(results)))

		# Extract relevant information from JSON file
		arr = extractInformation()
		print(
			"[+] Extracted relevant information from tweets - {} ".format(len(arr)))

		# Convert JSON to dataframe
		df = getDataframe(arr)
		print("[+] Converted information to dataframe ")

		# Save dataframe as CSV
		saveToCSV(df)
		print("[+] Saved as CSV with filename: {}".format(filename))

		print("[+] Loaded model")

		df1 = pd.DataFrame(predict(df))
		print("[+] Prediction done. DF1 size: {}".format(len(df1)))

		xml = convertToXML(df1)
		print("[+] Converted to XML")

		saveXML(xml)
		print("[+] Saved as XML")

		pushSolr(xml)
	else:
		print("[+] Solr database up to date!")


def main():
	while True:
		starttime = time.time()
		print("Updating... ")
		update()
		print("Done! Waiting for next minute... Elapsed:{}".format(time.time() - starttime))
		time.sleep(60.0 - ((time.time() - starttime) % 60.0))
		
if __name__ == "__main__":
	main()
