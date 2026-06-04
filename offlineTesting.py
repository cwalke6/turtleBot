# Summary
# Checks if a message is a x.com link, vxtwitter link, etc. 
# If it is it checks the database to see if it has already been seen.
# If true, it reacts to the message with a turtle, if not it stores it in the database.

# Database will be a hash table since we already have the hash at the end of the tweet.

# x.com alternatives: fixupx, vxtwitter,

import re
from datetime import datetime
import heapq

def removeOldTweets(h, s):
    # Get the current time epoch. (seconds)
    currTime_epoch = datetime.now().timestamp()
    secondsInWeek = 604800
    # Conver from ms to seconds
    while h and (currTime_epoch - (h[0][0] / 1000)) > secondsInWeek:
        tweetTime = h[0][0] / 1000
        print(f"{currTime_epoch} - {tweetTime} > {secondsInWeek}")
        print(f"{currTime_epoch - tweetTime} > {secondsInWeek}")
        # This tweet is a week old. Can remove it now.
        print(f"Tweet is old. Removing it.")
        tweetToRemove = heapq.heappop(h)
        s.remove(tweetToRemove[1])

# Emoji variables
turtleRaw = "🐢"
turteUnicode = "\U0001F422"

# Twitter/Snowflake decoder variables
twitterEpoch_ms = 1288834974657
regexPattern = r"(\d+)"
#link = "https://x.com/cookiecastleee/status/2062167289072615610?s=20"
# link = "https://x.com/jttojaybee/status/2056582358741004331"
link = "https://x.com/nikotaughtyou/status/2051052445107696107?s=46&t=Qe4miad8z-AUeQphNY5Skw"
# Heap to store (timestamp of tweets (ms), last 22 bits of snowflake)
tweetsHeap = []
seenTweets = set() 

if("x.com" in link):
    print(f"[mainLoop::on_message]: message has x.com in it.")
    match = re.search(regexPattern, link)
    if match:
        print(f"Here is the snowflake ID of the link: {match.group()}")
        snowflakeID = int(match.group())
        machineID = snowflakeID & 0x3FFFFF
        print(f"machine ID: {machineID}")
        tweetTimestamp_ms = snowflakeID >> 22
        print(f"snowflakeID >> 22 bits {tweetTimestamp_ms}")
        tweetTimestamp_ms = tweetTimestamp_ms + twitterEpoch_ms
        print(f"tweetTimestamp_ms: {tweetTimestamp_ms}")
        tweetTimestamp_s = tweetTimestamp_ms / 1000
        print(f"Date Time Timestamp: {datetime.utcfromtimestamp(tweetTimestamp_s).strftime('%Y-%m-%d %H: %M: %S')}")
        if snowflakeID not in seenTweets:
            seenTweets.add(snowflakeID)
            heapq.heappush(tweetsHeap, (tweetTimestamp_ms, snowflakeID))
        else:
            print("Seen tweet")

# TODO: Make global and have removeOldTweets() have no parameters.
removeOldTweets(tweetsHeap, seenTweets)

