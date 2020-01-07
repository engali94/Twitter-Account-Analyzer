# -*- coding: utf-8 -*-


# Setup
"""

# Import needed libraries

from google.colab import drive  # to mount Google Drive to Colab notebook
import tweepy                   # Python wrapper around Twitter API
import json
import pandas as pd
import csv
from datetime import date
from datetime import datetime
import time
import matplotlib.pyplot as plt

# Mounting Google Drive

drive.mount('/content/gdrive')
path = './gdrive/My Drive/datasets/twitter_analysis/'

"""# Twitter Data Collection

## Log into Twitter API
"""

# Load Twitter API secrets from an external file
secrets = json.loads(open(path + 'secrets.json').read())  

consumer_key = secrets['consumer_key']
consumer_secret = secrets['consumer_secret']
access_token = secrets['access_token']
access_token_secret = secrets['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

"""## Helper Functions

### Save JSON file
"""

# Helper function to save data into a JSON file
# file_name: the name of the data file you want to save on your Google Drive
# file_content: the data you want to save

def save_json(file_name, file_content):
  with open(path + file_name, 'w', encoding='utf-8') as f:
    json.dump(file_content, f, ensure_ascii=False, indent=4)

"""### Twitter API limit handling"""

# Helper function to handle twitter API rate limit

def limit_handled(cursor, list_name):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("\nCurrent number of data points in list = " + str(len(list_name)))
            print('Hit Twitter API rate limit.')
            for i in range(3, 0, -1):
              print("Wait for {} mins.".format(i * 5))
              time.sleep(5 * 60)
        except tweepy.error.TweepError:
            print('\nCaught TweepError exception' )

# update these for whatever tweet you want to process replies to
name = 'malkassabi'
tweet_id = '1212081182365622273'

replies=[]
cursor = tweepy.Cursor(api.search,q='to:'+name, result_type='recent', timeout=999999).items(1000)
for tweet in cursor:
    if hasattr(tweet, 'in_reply_to_status_id_str'):
        if (tweet.in_reply_to_status_id_str==tweet_id):
            replies.append(tweet)

# save_json('replies.json', replies)

with open(path + 'replies.csv', 'wb') as f:
    csv_writer = csv.DictWriter(f, fieldnames=('user', 'text'))
    csv_writer.writeheader()
    for tweet in replies:
        row = {'user': tweet.user.screen_name, 'text': tweet.text.encode('ascii', 'ignore').replace('\n', ' ')}
        csv_writer.writerow(row)

len(replies)

"""## Data Collection Functions

### Get all tweets
"""

# Helper function to get all tweets for a specified user
# NOTE:  This method only allows access to the most recent 3240 tweets
# Source: https://gist.github.com/yanofsky/5436496

def get_all_tweets(screen_name):

	# initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	# make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	
	# save most recent tweets
	alltweets.extend(new_tweets)
	
	# save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	
	# keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print("getting tweets before %s" % (oldest))
		
		# all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		
		# save most recent tweets
		alltweets.extend(new_tweets)
		
		# update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		print("...%s tweets downloaded so far" % (len(alltweets)))
	
	# transform the tweepy tweets into a 2D array that will populate the csv	
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text, tweet.favorite_count, 
	              tweet.in_reply_to_screen_name, tweet.retweeted] for tweet in alltweets]
	
	# write the csv	
	with open(path + '%s_tweets.csv' % screen_name, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["id","created_at","text","likes","in reply to","retweeted"])
		writer.writerows(outtweets)
	
	pass

"""### Get today's twitter stats"""

# Helper function to get today's numbers of followers and friends and store 
# them into a JSON file

def todays_stats(dict_name):
  info = api.me()
  followers_cnt = info.followers_count
  following_cnt = info.friends_count
  today = date.today()
  d = today.strftime("%b %d, %Y")
  if d not in dict_name:
    dict_name[d] = {"followers":followers_cnt, "following":following_cnt}
    save_json("follower_history.json", dict_name)
  else:
    print('Today\'s stats already exist')

"""### Get followers data"""

# Helper function to load follower objects into a list and save it into 
# a JSON file. 

def get_followers():
  followers = []

  cursor = tweepy.Cursor(api.followers, count=200).pages()
  for i, page in enumerate(limit_handled(cursor, followers)):
      print("\r"+"Loading"+ i % 5 *".", end='')
      followers += page

  followers = [x._json for x in followers]
  save_json('followers_data.json', followers)

"""### Get friends data"""

# Load friends into list

def get_friends():
  friends = []

  for i, page in enumerate(limit_handled(tweepy.Cursor(api.friends, count=200).pages(), friends)):
      print("\r"+"Loading"+ i % 5 *".", end='')
      friends += page

  friends = [x._json for x in friends]
  save_json('friends_data.json', friends)

"""## Data Collection Main Script"""

if __name__ == '__main__':
  #pass in the username of the account you want to download
  get_all_tweets("alihilal94")
  with open(path + 'follower_history.json') as json_file:
    history = json.load(json_file)
  todays_stats(history)
  get_followers()
  get_friends()

api.followers()

type(test)

"""# Analyzing tweets

## Load saved data from Google Drive
"""

# Load all saved tweets from @alihilal94
tweets = pd.read_csv(path + 'alihilal94_tweets.csv')

"""### Classify tweets"""

# Classify the type of each tweet (i.e. Tweet, Reply, or Retweet)

tweets.retweeted = tweets.text.apply(lambda x: True if 'RT @' in x else False)
tweets['in reply to'] = tweets['in reply to'].fillna('N/A')
tweets['type'] = tweets['in reply to'].apply(lambda x: 'Tweet' if x == "alihilal94" or x == 'N/A' else 'Reply')
tweets.loc[tweets.retweeted, 'type'] = 'Retweet'
tweets.to_csv(path + 'alihilal94_tweets.csv')

# Find the number of tweets in each type
print('Total number of tweets = {}'.format(len(tweets)))
print('\nNumber of tweets by')
tweets.groupby('type').count().id

# Find the average number of likes per tweet type
tweets.groupby('type').mean().likes

# Find and print the top 10 tweets by number of likes
top10 = tweets.sort_values('likes',ascending=False)
top10 = top10.reset_index(drop=True)
top10 = top10.head(10)

for i in range(len(top10)):
  print("{}) At {} likes:".format(i+1, top10.likes[i]))
  print(top10.text[i]+"\n")

# Find tweets with likes > 49 but < 100
# 49 = the average number of likes my tweets get
# 100 was arbitrarily chosen

tweets[((tweets.likes > 49) & (tweets.likes < 100))].sort_values('likes',ascending=False)

plot_data = tweets[tweets.type == "Tweet"]
plot_data = plot_data[['id','created_at','likes']]
plot_data['time'] = plot_data['created_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,6))
fig.suptitle('Tweets vs. Likes Received')
ax1.scatter(plot_data.time, plot_data.likes)
ax2.scatter(plot_data.time, plot_data.likes)
left = date(2018, 10, 1)
right = date(2020, 1, 1)
ax2.set_xlim(left=left, right=right);

"""#Analyzing followers

##Load Saved data from Google Drive
"""

followers = pd.read_json(path + 'followers_data.json') # Followers User ojbects

df = followers

df = df.fillna('Empty')

df = df.replace('','Empty')

# Create list of tags to identify each location
turkey_tags =['turkey', 'Türkiye', 'Ankara', 'İstanbul', 'deprem',  'istanbulhavalimanı', 'Kayseri']

saudi_tags = ['saudi', 'ksa', 'riyadh', 'jeddah', 'makkah', 'madina', 'dammam', 'khobar', 'السعودية', 'السعوديه', 'جدة', 'الرياض', 'الدمام', 'neom', 'eastern', 'riyad', 'riydah', 'med', 'jed',
              'jubail', 'المدينة', 'ابها', 'مكة', 'sa', 'k.s.a', 'qatif', 'medina', 'tabuk', 'dhahran', 'abha', 'hail', 'qassim', 'mecca', 'ruh', 'buraydah', 'الخبر', 'الشرقية', 'الحجاز', 'بريدة', 'القصيم', 'المملكة العربية', 'جده', 'مكه',
              'الحد_الجنوبي', 'الحرمين', 'نجد', 'الرّس', 'j town', 'جازان', 'unayzah', 'الخُبر', 'الظهران', 'تبوك', 'حائل', 'طيبة', 'المجمعة', 'yanbu', 'taif', 'baljurashi', 'الأحساء', 'jeedah', '966', 'suudi', 'أملج', 'اللهم احفظ بلادي', 'الجبيل',
              'سعودية', 'ينبع', 'ryiadh', 'الطائف', 'jdh', 'Alkharj', 'طويق', 'الباحة', 'أم الملح', 'Al Badai', 'البدائع', 'الدرعيه', 'к.ѕ.α', 'المنوره', 'Abu Arish', 'Alkhober', 'rio', '🇸🇦', 'ام الملح', 'فوق هام السحب']

gulf_tags = ['uae', 'kuwait', 'qatar', 'yemen', 'oman', 'bahrain', 'اليمن', 'الإمارات', 'الكويت', 'قطر', 'البحرين', 'عمان', 'abu dhabi', 'q8', 'الجزيره',
             'dubai', 'الامارات', 'مسقط', 'شبه الجزيرة', 'جزيرة العرب', 'al ain', 'kwt', 'u.a.e', 'حضرموت', 'alain', 'arabian island']

mena_tags = ['egypt', 'مصر', 'libya', 'ليبيا', 'iraq', 'العراق', 'sudan', 'syria', 'jordan', 'الأردن', 'morocco', 'tunisia',
             'algeria', 'mauritania', 'palestine', 'فلسطين', 'cairo', 'gaza', 'الوطن العربي', 'Algiers', 'Marrakech', 'Mansoura', 'Algérie', 'amman', 'rafah', 'الاردن', 'لبنان', 'غزة', 'egy', 'eg', 'سوريا', 'حلب', 'الجزائر',
             'khartoum', 'tunis', 'الإسكندرية', 'السودان', 'lebanon', 'irbid', 'Touggourt', 'ramallah', 'سطيف', 'عمّـان', 'الأسكندرية', 'العالم الإسلامي', 'بلد المليون شهيد', 'MENA']

us_tags = ['us', 'united', 'states', 'usa', 'أمريكا', 'los angeles', 'NY', 'IL', 'DC', 'boston', 'stanford', 'philadelphia', 'CT', 'new orleans', 'miami', 'u.s.a', 'omaha',
           'new york', 'manhattan', 'mn', 'menlo park', 'wa', 'az', 'sf', 'tx', 'pa', 'or', 'portola valley', 'bay area', 'cambridge', 'va', 'fl', 'ga', 'lincoln', 'irvine', 'detroit', 'halifax',
           'ohio', 'nm', 'تكساس', 'co', 'oh', 'nc', 'الامريكية', 'cypress', '92108', 'West Lafayette', 'Utah']

uk_tags = ['uk', 'london', 'leeds', 'new castle', 'manchester', 'liverpool', 'england', 'ireland', 'scotland', 'glasgow']

euro_tags = ['paris', 'france', 'spain', 'munich', 'italy', 'netherlands', 'nederland', 'Deutschland', 'germany', 'berlin', 'finland', 'switzerland', 'sweden', 'stuttgart', 'Malmö', 'Sverige', 'Rotterdam']

canada_tags =['canada', 'british columbia', 'ontario', 'Montréal', 'calgary']



# Create logical masks to clean up data
saudi = df.location.str.contains('|'.join(saudi_tags), case=False)
gulf = df.location.str.contains('|'.join(gulf_tags), case=False)
mena = df.location.str.contains('|'.join(mena_tags), case=False)
us = df.location.str.contains('|'.join(us_tags), case=False)
uk = df.location.str.contains('|'.join(uk_tags), case=False)
euro = df.location.str.contains('|'.join(euro_tags), case=False)
canada = df.location.str.contains('|'.join(canada_tags), case=False)
turkey = df.location.str.contains('|'.join(turkey_tags), case=False)
empty = df.location.str.contains('Empty')
other = saudi | gulf | mena | us | uk | euro | canada | turkey | empty
other = ~other

# Clean up data
df.loc[gulf, 'location'] = 'Gulf'
df.loc[mena, 'location'] = 'MENA'
df.loc[us, 'location'] = 'US'
df.loc[uk, 'location'] = 'UK'
df.loc[euro, 'location'] = 'Europe'
df.loc[canada, 'location'] = 'Canada'
df.loc[turkey, 'location'] = 'Turkey'
df.loc[saudi, 'location'] = 'Saudi Arabia'
df.loc[empty, 'location'] = 'Empty'
df.loc[other, 'location'] = 'Other'

print('Number of unique locations before clean up: ' + str(len(followers.location.unique())))
print('Number of unique locations after clean up: ' + str(len(df.location.unique())))

print('Total number of followers: {}\n'.format(len(followers)))

print('Followers by')
df.groupby('location').count().sort_values('id',ascending=False).id

# List the unique locations under Other

ids = df[df.location == 'Other'].id
followers[followers.id.isin(ids)].location.unique()

print("Number of followers who have more than 30k followers: {}".format(len(df.loc[df.followers_count >= 3e4])))
print('Number of verified followers: {}'.format(len(df[df.verified == True])))

"""#Analyzing following

## Load Saved Data from Google Drive
"""

following = pd.read_json(path + 'friends_data.json')       # Friends User ojbects

df = following

df = df.fillna('Empty')

df = df.replace('','Empty')

# Create list of tags to categorize following
gov_url_tags =['.gov', 'neom', 'qiddiya', '.sa', '.com.sa', '.tr', '.state', '.iq', '.ae']
gov_bio_tags = ['وزير', 'نائب مدير', 'وكيل', 'وزارة', 'محافظ', 'هيئة', 'مدير', 'minster', 'bakan', 'member']
academic_url_tags =['.edu']
academic_bio_tags =['prof', 'professor', 'research', 'أستاذ']
vc_tags =  ['fund', 'vc', 'partner', 'investor', 'venture', 'gp']
ai_tags =  ['ai', 'ml', 'deep learning', 'machine learning', 'vision', 'keras', 'tensorflow', 'Data Scientist', 'Data Science', 'nlp', 'xgboost', 'علم البيانات']
product_tags =  ['product', 'cpo', 'design', 'PM']
fitness_tags = ['fitness', 'muscle', 'nba']
ceo_tags = ['ceo', 'الرئيس التنفيذي']
magazine_tags =  ['forbes', 'techcrunch', 'inc', 'nat geo', 'harvardbiz', 'engadget', 'freakonomics', 'tedtalks', 'reutersbiz', 'huffpost', 
                  'wsj', 'business', 'theeconomist', 'bw', 'businessinsider', 'cnn', 'time', 'popmech', 'Entrepreneur', 'fastcompany', 'alarabiya']
writer_tags =  ['writer', 'editor', 'author', 'journalist', 'skinny canadian', 'news', 'report', 'cover', 'كاتب', 'صحفي', 'أكتب', 'writing', 'correspondent']
energy_tags = ['energy', 'exxon', 'أرامكو']
startup_tags = ['founder', 'yc', 'ycw', 'co-founder', 'مؤسس']
programmer_tags = ['Python','Swift', 'Android','iOS','Java', 'developer', 'software', 'linux', 'hacker', 'هاكر', 'مطور', 'مبرمج', '.net', 'php', 'laravel', 'gnu', 'engineer', 'cto']


# Create logical masks to clean up data

# Based on URL
gov_url = df['url'].str.contains('|'.join(gov_url_tags), case=False)
academic_url = df['url'].str.contains('|'.join(academic_url_tags), case=False)

# Based on twitter profile bio
gov_bio = df['description'].str.contains('|'.join(gov_bio_tags), case=False)
academic_bio = df['description'].str.contains('|'.join(academic_bio_tags), case=False)
vc = df['description'].str.contains('|'.join(vc_tags), case=False)
ai = df['description'].str.contains('|'.join(ai_tags), case=False)
product = df['description'].str.contains('|'.join(product_tags), case=False)
writer = df['description'].str.contains('|'.join(writer_tags), case=False)
fitness = df['description'].str.contains('|'.join(fitness_tags), case=False)
energy = df['description'].str.contains('|'.join(energy_tags), case=False)
startup = df['description'].str.contains('|'.join(startup_tags), case=False)
ceo = df['description'].str.contains('|'.join(ceo_tags), case=False)
programmer = df['description'].str.contains('|'.join(programmer_tags), case=False)

# Based on twitter ID
magazine = df['screen_name'].str.contains('|'.join(magazine_tags), case=False)

# Based on a combination 
gov = gov_url | gov_bio
academic = academic_url | academic_bio
media = writer | magazine

# Clean up data
df.loc[gov, 'Category'] = 'Gov'
df.loc[academic, 'Category'] = 'Academic'
df.loc[vc, 'Category'] = 'VC'
df.loc[ai, 'Category'] = 'AI'
df.loc[product, 'Category'] = 'Product'
df.loc[media, 'Category'] = 'Media (writer/magazine)'
df.loc[fitness, 'Category'] = 'Fitness'
df.loc[energy, 'Category'] = 'Energy'
df.loc[startup, 'Category'] = 'Startup'
df.loc[ceo, 'Category'] = 'CEO'
df.loc[programmer, 'Category'] = 'Programmer'
df.fillna('Other',inplace=True)

print('Total number of users I\'m following: {}\n'.format(len(following)))

print('Following by')
df.groupby('Category').count().id.sort_values(ascending=False)

# List the users under Other

ids = df[df.Category == 'Other'].id
following[following.id.isin(ids)][['screen_name','description']]

# Unfollow all users in the fitness category

fitness_df = df[df.Category == 'Fitness']

for _, row in fitness_df.iterrows():    # iterate over rows in the fitness data
  api.destroy_friendship(row['id'])     # use twitter api to unfollow based on id

"""# Analyzing History

## Load Saved Data from Google Drive
"""

history = pd.read_json(path + 'follower_history.json').transpose()     # Follower history dictionary
dates = history.index.strftime('%b %d')

# Plot the number of my followers over time

plt.bar(dates, history.followers, figure=plt.figure(figsize=(10,6)), width=0.4);
plt.ylim(8000, 1e4);
plt.title('Followers over time in 2019');

# Plot number of users I'm following over time

plt.bar(dates, history.following, figure=plt.figure(figsize=(10,6)), width=0.4);
plt.ylim(1.35e3, 1.48e3);
plt.title('Following over time in 2019');
