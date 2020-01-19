# Twitter Account Data Analysis

Using various Python libraries such as Pandas, tweetPy, JSON and matplotLib to take a sneak peek on your Twitter account using Google Colab.


# Setup

#### Open Google Colab and import the required Libs
``` python
    from google.colab import drive # to mount Google Drive to Colab notebook
    import tweepy # Python wrapper around Twitter API
    import json
    import pandas as pd
    import csv
    from datetime import date
    from datetime import datetime
    import time
    import matplotlib.pyplot as plt
```
#### Mounting Google Drive

create a new folder name it `dataset` then another inside it with `twitter_analysis` **Yo can change the directory as you like**
``` python
    drive.mount('/content/gdrive')
    path = './gdrive/My Drive/datasets/twitter_analysis/'
    #Follow the popup link and complete the autuorization  process
```

#  Twitter Data Collection

#### Login
In this section you  need to get your Twitter API  credentials then  load Twitter API secrets from an external file
``` python
    secrets = json.loads(open(path + 'secrets.json').read())
    consumer_key = secrets['consumer_key']
    consumer_secret = secrets['consumer_secret']
    access_token = secrets['access_token']
    access_token_secret = secrets['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
```
####  Helper Functions
-  `save_json(file_name, file_content)`: Helper function to save data into a JSON file.
-  `file_name`: the name of the data file you want to save on your Google Drive
-  `file_content`: the data you want to save.
-  `limit_handled(cursor, list_name)`  Helper function to handle twitter API rate limit.

#### Data Collection Functions
-   `get_all_tweets(screen_name)` : Helper function to get all tweets for a specified user and write it to a csv file.
- `todays_stats(dict_name)` :  Helper function to get today's numbers of followers and friends and store them into a JSON file.
- `get_followers()`:  Helper function to load follower objects into a list and save them into a JSON file.
- `get_friends()`:  Load friends into list



# Analyzing tweets
- Load saved data from Google Drive
- Classify tweets

![Classification](https://github.com/engali94/Twitter-Account-Analysis/blob/master/assets/classification.png)
## Analyzing followers

## Analyzing following 

## Analyzing History


# About The Author
- [blog](https://www.alihilal.com/blog)
- [Twitter](https://twitter.com/alihilal94)
