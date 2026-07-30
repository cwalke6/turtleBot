# Summary
# Checks if a message is a x.com link, vxtwitter link, etc. 
# If it is it checks the database to see if it has already been seen.
# If true, it reacts to the message with a turtle, if not it stores it in the database.

# Database will be a hash table since we already have the hash at the end of the tweet.

# x.com alternatives: fixupx, vxtwitter,

import re
import discord
from datetime import datetime
import heapq
import sqlite3
import logging

with open("api_token.txt", "r") as f:
    DISCORD_API_TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

# Emoji variables
turtleRaw = "🐢"
turtleUnicode = "\U0001F422"

# Twitter/Snowflake decoder variables
twitterEpoch_ms = 1288834974657
regexPattern = r"status/(\d+)"
secondsInWeek = 604800

# Data structures to store tweets.
# Heap stores (timestamp of tweets (s), last 22 bits of snowflake)
tweetsHeap = []
seenTweets = set()

# Leaderboard Database
conn = sqlite3.connect("leaderboard.db")
cursor = conn.cursor()

logger = logging.getLogger(__name__)
logging.basicConfig(filename="turtlebot.log", level=logging.INFO)

# Used to prune the Heap. If a week old removes from both data structures.
def removeOldTweets():
    # Get the current time epoch. (Secs)
    currTime_epoch = datetime.now().timestamp()

    while tweetsHeap and (currTime_epoch - (tweetsHeap[0][0])) > secondsInWeek:
        logger.info(f"[removeOldTweets]: Tweet is a week old. Removing")
        tweetToRemove = heapq.heappop(tweetsHeap)
        seenTweets.remove(tweetToRemove[1])

def checkMessage(message):
    twitterLinks = ["https://x.com/", "https://twitter.com/", "https://fixupx.com/",
                    "https://vxtwitter.com/", "https://girlcockx.com/"] 
    for link in twitterLinks:
        if link in message:
            return True

def updateLeaderboard(userID):
    # 1. Create the table if it does not exist.
    cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard (user_id TEXT UNIQUE, score INTEGER);")
    # 2. Check if the user is in the data base's table
    cursor.execute("INSERT INTO leaderboard (user_id, score) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET score = score + 1;", (userID,))
    conn.commit()

# Discord Logic
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"[mainLoop::on_ready()]: We have logged in as {client.user}")

@client.event
async def on_message(message):
    removeOldTweets()

    # Leaderboard Logic.
    if message.content == "!turtleleaderboard":
        logger.info(f"[mainLoop::show_leaderboard]: Showing leaderboard.")
        cursor.execute("SELECT user_id, score FROM leaderboard ORDER BY score DESC;")
        rows = cursor.fetchall()
        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (user_id, score) in enumerate(rows):
            user = await client.fetch_user(int(user_id))
            prefix = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{prefix} **{user.display_name}** - {score} turtles")

        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="\n".join(lines),
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)

    currTime_epoch = datetime.now().timestamp()
    turtleSend = False
    # Check if the message is a link
    if("https://" in message.content and checkMessage(message.content)):
        logger.info(f"[on_message]: message is a twitter link.")
        logger.info(f"[on_message]: raw message: {message.content}")
        match = re.search(regexPattern, message.content)
        if match:
            logger.info(f"[on_message]: Snowflake ID of link: {match.group()[7:26]}")
            snowflakeID = int(match.group()[7:26])
            machineID = snowflakeID & 0x3FFFFF
            tweetTimestamp_ms = snowflakeID >> 22
            tweetTimestamp_ms = tweetTimestamp_ms + twitterEpoch_ms
            tweetTimestamp_s = tweetTimestamp_ms / 1000
            if((currTime_epoch - tweetTimestamp_s) < secondsInWeek):
                if snowflakeID not in seenTweets:
                    seenTweets.add(snowflakeID)
                    heapq.heappush(tweetsHeap, (tweetTimestamp_s, snowflakeID))
                else:
                    logger.info(f"[on_message]: Seen Tweet, WOULD BE A TURTLE")
                    turtleSend = True
                    # Have to add to leaderboard.
                    updateLeaderboard(message.author.id)
            else:
                logger.info(f"[on_message]: Tweet is too old. Not adding.")

    # Action.
    if(not turtleSend):
        return

    await message.add_reaction(turtleUnicode)

# To be imported from a .gitignore file.
client.run(DISCORD_API_TOKEN)

