# CZ4034 - INFORMATION RETRIEVAL PROJECT

**Demo video:  https://youtu.be/jRqb7Z6IR5M**

**Overview** 

In this assignment, we crawled a text corpus of 10,000 tweets off Twitter and developed a web application to retrieve tweets that are of relevance
to the users. We applied concepts of machine learning to classify and add another dimension of filters for better information retrieval. Our objective is to
improve upon the current implementation of search on Twitter, by providing a user-friendly and intuitive way of retrieving information of interest to the users.


**Setup instructions**

* For Solr: 
  - `cd solr-7.1.1`
  - `bin\solr start` 
  - `bin\solr stop -all` 
  
* For Webapp:
  - `cd webapp`
  - `npm install`
  - `npm run dev`
  
* For updater, please supply the consumer and access key pairs and run when both Solr and Webapp are running: 
  - `python updater.py`
  
* Python dependencies: 
  - Tweepy version: 3.6.0 
  - pandas version: 0.23.4 
  - numpy version: 1.15.2 
  - nltk version: 3.3 
  - sklearn version: 0.20.1 
  - matplotlib version: 3.0.0 
  - requests version: 2.13.0 
  - json version: 2.0.
  
Additionally, you may find the following commands useful 
  - Deleting all indexed entries: `curl http://localhost:8983/solr/ir/update?commit=true -X POST -H "Content-Type: text/xml" --data-binary "<delete><query>*:*</query></delete>"` 
  - Adding back the original 10,000 tweets: `java -Dc="ir" -jar bin/post.jar total.xml` 
