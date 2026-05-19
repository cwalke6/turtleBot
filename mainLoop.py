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

turtleRaw = "🐢"
turteUnicode = "\U0001F422"

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[mainLoop::on_ready()]: We have logged in as {client.user}")

@client.event
async def on_message(message):
    turtleSend = False
    # Check if the message is a link
    # TODO: Might be faster to just check if it is a link initially, then check substrings?
    if("x.com" in message.content):
        print(f"[mainLoop::on_message]: message has x.com in it.")
    # Check if the message is within the database.
    # TODO: Get the hash from the string, REGEX?
    # TODO: Interface the data base
    # Action.
    if(!turtleSend):
        return

    await message.add_reaction(turtleUnicode)
    await message.channel.send('That deserves a turtle!')


# To be imported from a .gitignore file.
client.run(DISCORD_API_TOKEN)

