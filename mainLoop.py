# Summary
# Checks if a message is a x.com link, vxtwitter link, etc. 
# If it is it checks the database to see if it has already been seen.
# If true, it reacts to the message with a turtle, if not it stores it in the database.

# Database will be a hash table since we already have the hash at the end of the tweet.

# x.com alternatives: fixupx, vxtwitter,

import discord

intents = dicord.Intents.default()
intents.message_content = True
intents.reactions = True

# Emoji variables
turtleRaw = "🐢"
turteUnicode = "\U0001F422"

# Twitter/Snowflake decoder variables
twitterEpoch = 1288834974657
regexPattern = r"(\d+)"
secondsinWeek = 6040800

# Data structures to store tweets.
# Heap stores (timestamp of tweets (s), last 22 bits of snowflake)
tweetsHeap = []
seenTweets = set()


# Used to prune the Heap. If a week old removes from both data structures.
def removeOldTweets():
    # Get the current time epoch. (Secs)
    currTime_epoch = datetime.now().timestamp()

    while tweetsHeap and (currTime_epoch - (tweetsHeap[0][0])) > secondsInWeek:
        print(f"[mainLoop::removeOldTweets] Tweet is a week old. Removing")
        tweetToRemove = heapq.heappop(tweetsHeap)
        seenTweets.remove(tweetToRemove[1])


# Discord Logic
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[mainLoop::on_ready()]: We have logged in as {client.user}")

@client.event
async def on_message(message):
    turtleSend = False
    # Check if the message is a link
    # TODO: Might be faster to just check if it is a link initially, then check substrings?
    # I am sure there is some python helper function to check this. Or discord.
    if("x.com" in message.content):
        # TODO: Get an actual logger helper functions.
        print(f"[mainLoop::on_message]: message has x.com in it.")
        match = re.search(regexPattern, message.content)
        if match:
            print(f"[mainLoop::on_message]: Snowflake ID of link: {match.group()}")
            snowflakeID = int(match.group())
            machineID = snowflakeID & 0x3FFFFF
            tweetTimestamp_ms = snowflakeID >> 22
            tweetTimestamp_ms = tweetTimestamp_ms + twitterEpoch_ms
            tweetTimestamp_s = tweetTimestamp_ms / 1000
            if snowflakeID not in seenTweets:
                seenTweets.add(snowflakeID)
                heapq.heappush(tweetsHeap, (tweetTimestamp_s, snowflakeID))
            else:
                print(f"[mainLoop::on_message]: Seen Tweet")
                turtleSend = True

    # Action.
    if(!turtleSend):
        return

    await message.add_reaction(turtleUnicode)
    await message.channel.send('That deserves a turtle!')


# To be imported from a .gitignore file.
client.run(DISCORD_API_TOKEN)

