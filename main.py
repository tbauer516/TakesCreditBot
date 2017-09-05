# TakesCreditBot takes credit for the 'good bot' statements made by
# others in reference to a bot that actually provides some use.
# Created by /u/tbauer516
# License: MIT License

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from random import randint

import os
import praw
import time
import re
import requests
import bs4
import sys

filename = 'commented.txt'
masterAccount = 'tbauer516'

apiTimeout = 60
numComments = 250
subredditNames = ['test']
# 'ShowerThoughts', 'photoshopbattles', 'InternetIsBeautiful', 'mildlyinteresting'

myCommentKarma = None
commentKarmaThreshold = 0

responses = [
    'Thank you, glad my effort can be appreciated.',
    'Thanks, just doing my best to be helpful.',
    'Thanks, I put a lot of hard work into this.'
]

userBotRegex = '(?i)bot'
commentPraiseRegex = '(?i)good\sbot[.]{0,3}'

previousComments = set()

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

def authenticate():
    print('Authenticating...\n')
    reddit = praw.Reddit('TakesCreditBot', user_agent = 'web:takes-credit-bot:v0.1 (by /u/tbauer516)')
    print('Authenticated as {}\n'.format(reddit.user.me()))
    return reddit


def hasDownvotesToDisable(reddit):
    myCommentKarma = int(reddit.user.me().comment_karma)
    return myCommentKarma < commentKarmaThreshold


def sendExitPM(reddit, user):
    print('Sending exit PM to ' + user)
    reddit.redditor(user).message('Bot Has Been Disabled',
        'TakesCreditBot has reached a large number of '
        + ' downvotes and has thus been shut down until '
        + ' human action takes place to re-enable it.')


def isCommentMatch(comment):
    match = re.findall(commentPraiseRegex, comment.body)
    return match


def isUserBot(user):
    # TODO: add more criteria for determining a bot
    if (re.search(userBotRegex, user.name)):
        return True
    # TODO: remove for when we actually want to filter on who is and is not a bot
    return True
    return False


def isParentCommentUserBot(comment):
    parent = comment.parent()
    return isUserBot(parent.author)


def isCommentNew(comment):
    return not comment.id in previousComments


def replyToComment(comment):
    print('replying to: ' + comment.author.name)
    comment.reply(responses[randint(0, len(responses) - 1)])
    previousComments.add(comment.id)


def saveCommentsToFile():
    with open(path, 'w+') as commentedFileObj:
        for item in previousComments:
            commentedFileObj.write(item)


def loadCommentsFromFile():
    with open(path, 'r') as commentedFileObj:
        for item in commentedFileObj.read().splitlines():
            previousComments.clear()
            previousComments.add(item)


def operateOnSingleComment(comment):
    match = isCommentMatch(comment)
    if match:
        print('\n')
        print(comment.author.name + ' praised a bot with comment ID: ' + comment.id)

        if (not isCommentNew(comment)):
            return
        print('comment is new')

        if (not isParentCommentUserBot(comment)):
            return
        print('parent is a bot')
        
        replyToComment(comment)


def runBot(reddit):
    print('Getting {} comments...\n'.format(numComments))
    for comment in reddit.subreddit(', '.join(subredditNames)).comments(limit = numComments):
        operateOnSingleComment(comment)


def runTest(reddit):
    print('running test')
    for comment in reddit.submission(id = '6vf2av').comments.list():
        operateOnSingleComment(comment)


def main():
    reddit = authenticate()
    loadCommentsFromFile()
    while True:
        runBot(reddit)
        saveCommentsToFile()
        if (hasDownvotesToDisable(reddit)):
            sendExitPM(reddit, masterAccount)
            break

        print('Waiting {} seconds...\n'.format(apiTimeout))
        time.sleep(apiTimeout)


def test():
    reddit = authenticate()
    runTest(reddit)


if __name__ == '__main__':
    args = sys.argv
    if (len(args) == 1):
        main()
    elif (args[1] == 'test'):
        test()