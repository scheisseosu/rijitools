import requests
import datetime
from datetime import timedelta, datetime, time
from bs4 import BeautifulSoup

class Board(object):
    def __init__(self, name, url, pages=0):
        self.name = name
        self.url = url
        self.pages = pages
        self.topics = []
        self.num_topics = 0
        self.num_posts = 0 #topic posts AND replies included
    
    def add_topic(self, top):
        self.topics.append(top)
        self.num_topics += 1
        self.num_posts += len(top)

    #Get the url of a given page on the board
    def page_url(self, page_num):
        #base case: first page is normal url
        if page_num==1:
            return self.url
        
        spliturl = self.url.split("-")
        spliturl[1] = '-'+spliturl[1] #replace hyphen used to split base url

        page_identifier = "p"+str(50*(page_num-1))
        return spliturl[0]+page_identifier+spliturl[1]
    
    def __repr__(self):
        return f"Rijihuudu Board \"{self.name}\" with {self.num_posts} posts at {self.url}"

class Topic(object):
    def __init__(self, url, title, description, content, author):
        self.url = url
        self.title = title
        self.time = None
        self.content = content
        self.author = author
        self.replies = []
    
    def add_reply(self, rep):
        self.replies.append(rep)

    def set_time(self, timestr):
        self.time = get_datetime(timestr)

    def __len__(self):
        return len(self.replies)+1 #count topic post + num replies

    def __repr__(self):
        return f"Topic {self.title} by {self.author} at {self.time}"

class Reply(Topic):
    def __init__(self, title, content, author, op):
        Topic.__init__(self, op.url, title, None, content, author)
        self.reply_to = op
    
    def __repr__(self):
        return f"Reply {self.title} by {self.author} at {self.time}"

def get_datetime(timestr):

    timestr = timestr.split(" ")
    if timestr[0] == "Today":
        date = datetime.today()
        timestr = timestr[2:]
    elif timestr[0] == "Yesterday":
        date = datetime.today() - timedelta(days=1)
        timestr = timestr[2:]
    else:
        date = datetime.strptime(" ".join(timestr[1:4]), "%b %d, %Y")
        timestr = timestr[4:]

    
    hourmin = timestr[0].split(":")
    hour = int(hourmin[0])
    minute = int(hourmin[1])
    
    daycycle = timestr[1] #am or pm
    #convert to 24h
    if hour == 12:
        hour -= 12
    if daycycle == "pm":
        hour += 12

    timeob = time(hour=hour, minute=minute)

    dt = datetime.combine(date, timeob)
    return dt

if __name__ == "__main__":
    print(get_datetime("Today at 12:21 am"))