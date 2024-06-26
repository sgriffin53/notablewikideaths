import wikipedia
import datetime
import os
import json
import sys
import praw
import time

credentials = 'client_secrets.json'
with open(credentials) as f:
    creds = json.load(f)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])

print(reddit)
print(reddit.auth.scopes())
in_right_month = False
in_right_day = False
x = datetime.datetime.now()
already_posted = []
if os.path.exists('already_posted.txt'):
    ff = open('already_posted.txt','r', encoding='utf-8')
    lines = ff.readlines()
    for line in lines:
        line = line.replace("\n","").strip()
        already_posted.append(line)
    ff.close()
while True:
    ff_already_posted = open('already_posted.txt', 'a', encoding='utf-8')
    in_right_day = False
    in_right_month = False
    cur_year = x.strftime("%Y")
    page = wikipedia.page('Deaths in ' + cur_year, auto_suggest=False)
    lines = page.content.split("\n")
    cur_month = x.strftime("%B")
    cur_day = x.strftime('%d')
    for line in lines:
        #if in_right_day: print(in_right_month, line)
        if '==' in line:
            title = line.replace('== ', '').replace(' ==', '')
            if title == cur_month:
                in_right_month = True
        if '===' in line:
            if in_right_month:
                title = line.replace('=== ','').replace(' ===', '')
                if title != cur_day and in_right_day:
                    #pass
                    in_right_day = False
                    break
                elif title == cur_day:
                    in_right_day = True
        #print(line + "\n")
        #print(in_right_day, line)
        if in_right_day:
            if ',' in line:
                name = line.split(',')[0]
                age = line.split(',')[1].replace(' ','')
                info = line.split(',')[2:100]
                new_info = ''
                i = 0
                for item in info:
                    i+=1
                    if i != 1: new_info += ","
                    new_info += item
                info = new_info.strip()
                url = 'https://en.wikipedia.org/wiki/' + name
                url = url.replace(" ", "%20")
                if url in already_posted: continue
                print("Name:", name)
                print("Age:", age)
                print("Info:", info)
                print("URL:", url)
                ff_already_posted.write(url + "\n")
                already_posted.append(url)
                subreddit = reddit.subreddit('NotableWikiDeaths')
                selftext = name
                title = name + " has passed away at age " + age + ", " + info
                result = subreddit.submit(title, url=url)
                print(title, result)
                #print(title)
    print("Trying again in 5 minutes.")
    time.sleep(300)
    ff_already_posted.close()