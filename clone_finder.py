import praw
from alive_progress import alive_bar as aliveBar
from datetime import datetime
from gi import require_version
require_version('Notify', '0.7')
from gi.repository import Notify
from os import mkdir
from os.path import isfile, isdir
from sys import platform
from time import time, sleep
from typing import Dict, NoReturn
global Globals

# Returns the current time in human-readable format
def getTime(timeToFind: float) -> str:
    return datetime.fromtimestamp(timeToFind).strftime("%Y-%m-%d %H:%M:%S")

# Logs a clone / potential clone to the log file.
def logPost(lines: Dict) -> NoReturn:
    global Globals
    
    for line in lines:
        
        # Check if line already in log file
        try:
            with open("data/cloneLog.txt", "r") as lineList:
                if line + "\n" in lineList.readlines():
                    return True
        
        # Create data directory if it is absent
        except FileNotFoundError:
            if not isdir("data"): mkdir("data")
            elif not isfile("data/cloneLog.txt"): pass
        
        print(f"{getTime(post.created_utc)} - " + line)
        
        # Write out to log file, creating it if it's absent
        with open("data/cloneLog.txt", "at+") as log:
            log.write(f"At {getTime(post.created_utc)}\n")
            log.write(line+"\n")
            
def checkPost(post: praw.models.Submission) -> NoReturn:
    global Globals
    
    # If there is no flair and the title matches the title of the previous,
    # post, then the post is a clone
    if post.link_flair_text is None and post.title == Globals.postData["previousPostTitle"]:
        Notify.Notification.new("Found cloned post.").show()
        logPost(
            [
                f"Found cloned post, URL at: https://reddit.com{post.permalink}",
                f"URL of previous post at: {previousPostURL}"
            ]
        )
        
    # If there is no flair and the post is older than the wait time,
    # it still could be a clone, as all posts should be flaired very quickly
    elif post.link_flair_text is None and (time() - post.created_utc) > Globals.WAIT:
        Notify.Notification.new("Found unflaired post, could be clone.").show()
        logPost([f"Found unflaired post, could be clone. URL at: https://reddit.com{post.permalink}"])
    
    elif Globals.DEBUG:
        logPost(["Skipping post at: https://reddit.com{post.permalink}."])

# Class for all important variables
class Globals:
    def __init__(self):
        self.DEBUG = False
        self.postData = {
                "firstPostURL": "",
                "previousPostTitle": "",
                "previousPostURL": ""
            }
        self.skip = False
        self.VERBOSE = False
        self.VERSION = "0.5.1"
        self.WAIT = 30
    
    def setPreviousPost(self, data: Dict) -> NoReturn:
        for key in self.postData:
            if not key == "firstPostURL": self.postData[key] = data[key]

# Initiate Globals, notifications, and Reddit instance
Globals = Globals()
Notify.init("Clone Finder")
Reddit = praw.Reddit("tcf", user_agent=platform+":tcf:v"+Globals.VERSION+" (by /u/MurdoMaclachlan)")

print(f"Running Clone Finder version {Globals.VERSION} with debug set to {Globals.DEBUG}.")

while True:
 
    # Fetch posts
    print("Fetching posts...")
    postList = Reddit.subreddit("transcribersofreddit").new(limit=500)
    print("Posts fetched; generating list...")
    
    
    for post in postList:
        
        # Check to see if the first post is the same as it was last loop
        # Skip this cycle if this is the case
        if f"https://reddit.com{post.permalink}" == Globals.postData["firstPostURL"]:
            print("No new posts since last check, skipping cycle.")
            if Globals.VERBOSE: Notify.Notification.new("Skipping cycle.").show()
            Globals.skip = True
            break
        
        # Else set new first post, continue to check all posts
        else:
            Globals.skip = False
            Globals.postData["firstPostURL"] = f"https://reddit.com{post.permalink}"
            checkPost(post)
            break
    
    if not Globals.skip:
        
        # Set up necessary variables
        Globals.setPreviousPost({"previousPostTitle": "", "previousPostURL": ""})
            
        print("Checking posts...")
        
        # Check all posts
        with aliveBar(500, spinner='classic', bar='classic', enrich_print=False) as progress:
            
            for post in postList:
                
                checkPost(post)
                
                # Set up for next loop
                Globals.setPreviousPost(
                    {
                        "previousPostTitle": post.title,
                        "previousPostURL": f"https://reddit.com{post.permalink}"
                    }
                )
            
                progress()
                
        print(f"Finished checking all posts, waiting {Globals.WAIT} seconds.")
    
    else:
        print(f"Waiting {Globals.WAIT} seconds.")

    sleep(Globals.WAIT)
