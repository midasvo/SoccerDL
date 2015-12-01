import requests
from bs4 import BeautifulSoup
import time
import praw
from urllib.parse import urlparse
import urllib.request
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

DB_FILE = 'db.txt'
VIDEOS_DIR = 'videos'
LIMIT = 120
REDDIT_USERNAME = "username"
REDDIT_PASSWORD = "password"
videoList = []

def loginToReddit():
    r = praw.Reddit('/u/username soccer information worker')
    r.login(username=REDDIT_USERNAME, password=REDDIT_PASSWORD, disable_warning=True)
    already_done = []
    return r

def downloadVideo(url_part, filename):
    url = 'http:' + url_part
    print("[DOWNLOAD] '"+filename)
    urllib.request.urlretrieve(url, VIDEOS_DIR+'/'+filename)
    print(" ...Done")
    videoList.append(filename)

    writeToDB(filename)


def writeToDB(filename):
    file = open(DB_FILE, "a")
    file.write(filename+"\n")
    file.close()

def fileInDB(filename):
    found = False
    file = open(DB_FILE, "r")
    filelist = file.readlines()
    file.close()

    if filename+'\n' not in filelist:
        found=False
    else:
        found=True
    return found

# does not work yet
def createCompilation(videoList):
    files = sorted( os.listdir("videos/") )
    print(files)
    clips = [ VideoFileClip('videos/%s'%f) for f in files]
    video = concatenate_videoclips(clips)
    video.write_videofile("demos.avi", codec="mpeg4")

def getVideoURL(submission):
    req = requests.get(submission.url)
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "html.parser")
        videos = soup.video
        vidS = videos.source['src']
        title = submission.title.replace("/", "")
        if(fileInDB(title+'.webm')):
            print("[EXCLUDE] '"+title+"' already in "+DB_FILE)
        else:
            downloadVideo(vidS, title+'.webm')
    else:
        print('Video has been deleted.. You may find a mirror in the comments: ' + submission.link)

def determineSource(submission):
    parsed = urlparse(submission.url)
    if parsed.netloc == "streamable.com":
        getVideoURL(submission)
    elif parsed.netloc == "gfycat.com":
        getVideoURL(submission)

def getSubmissions(subr, type, amount, r):
    print("Getting submissions from /r/" + subr)
    subreddit = r.get_subreddit(subr)
    for submission in subreddit.get_hot(limit=amount):
        determineSource(submission)



def createDB():
    if not os.path.exists('db.txt'):
        print("Creating database file")
        open(DB_FILE, 'w').close()
        file = open(DB_FILE, "a")
        file.write("<--- SOCCERDL DATABASE FILE --->\n")
        file.close()
    else:
        print("Using existing database file")

def createVideosDirectory():
    if not os.path.exists(VIDEOS_DIR):
        print("Creating videos directory")
        os.makedirs(VIDEOS_DIR)
    else:
        print("Already have videos dir")

def main():
    print("Starting SoccerDL")
    createVideosDirectory()
    createDB()
    r = loginToReddit()
    getSubmissions('soccer', 'hot', LIMIT, r) # Not yet implemented categories.
main()
