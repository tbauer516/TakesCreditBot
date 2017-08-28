# TakesCreditBot takes credit for the 'good bot' statements made by
# others in reference to a bot that actually provides some use.
# Created by /u/tbauer516
# License: MIT License

####################
# import all libraries here
# includes other setup of widely used variables
####################
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import praw
import time
import re
import requests
import bs4
import sys

# local user account the file will run on
locUser = 'tbauer516'
# location of file where id's of already visited comments are maintained
path = '/home/' + locUser + '/TakesCreditBot/commented.txt'

# regex used to find the comments we are looking for
commentRegex = '[gG][oO]{2}[dD]\s[bB][oO][tT][.]{0,3}'
# timeout between gathering comment chunks
apiTimeout = 60

# responses stored in a list
responses = ['Thank you, glad my effort can be recognized.']

####################
# used to authenticate with Reddit, then return an instance used
# to interact with the reddit API
####################
def authenticate():
    print('Authenticating...\n')
    reddit = praw.Reddit('TakesCreditBot', user_agent = 'web:takes-credit-bot:v0.1 (by /u/tbauer516)')
    print('Authenticated as {}\n'.format(reddit.user.me()))
    return reddit

####################
# used to determine if the comment passed is of interest to us
####################
def isCommentMatch(comment):
    match = re.findall(commentRegex, comment.body)
    return match

####################
# used to determine if the user passed is a bot
####################
def isUserBot(user):
    # TODO: add more criteria for determining a bot
    if (re.search('[bB][oO][tT]', user.name)):
        return True
    return False

####################
# parse a single comment
####################
def parseComment(comment):
    parent = comment.parent()
    if (isUserBot(parent.author)):
        print('parent is a bot')
        print(comment.author.name + ' praised a bot with comment ID: ' + comment.id)

####################
# adds an entry to the tracking file of comments that have
# been previously commented on
####################
def updateCommentTrackerFile(comment):
    commentedFileObj = open(path,'a+')

    if comment.id not in commentedFileObj.read().splitlines():
        print('comment is new...posting reply\n')
        # TODO: uncomment below lines
        # comment.reply(responses[0])
        # commentedFileObj.write(comment.id + '\n')

    commentedFileObj.close()
    time.sleep(10)

####################
# function to match, read and track a single comment
####################
def operateOnSingleComment(comment):
    match = isCommentMatch(comment)
    if match:
        parseComment(comment)
        updateCommentTrackerFile(comment)

####################
# single loop instance that runs the bot
####################
def runBot(reddit):
    print('Getting 250 comments...\n')
    
    for comment in reddit.subreddit('test').comments(limit = 250):
        operateOnSingleComment(comment)

    print('Waiting {} seconds...\n'.format(apiTimeout))
    time.sleep(apiTimeout)

####################
# function that can be called to run a test on a single comment
# without running a loop
####################
def runTest(reddit):
    print('running test')
    for comment in reddit.submission(id = '6vf2av').comments.list():
        operateOnSingleComment(comment)

####################
# loop that calls the main loop above
####################
def main():
    reddit = authenticate()
    while True:
        runBot(reddit)

def test():
    reddit = authenticate()
    runTest(reddit)


if __name__ == '__main__':
    args = sys.argv
    if (len(args) == 1):
        main()
    elif (args[1] == 'test'):
        test()