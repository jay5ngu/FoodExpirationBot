# to run file from command terminal (windows), type "py bot.py"
# to run file from command terminal (mac), type "python3 bot.py"
import discord
from discord.ext import tasks, commands
import datetime
import json

content = None

try:
    # loads information from secret.json file
    with open('secret.json') as file:
        content = json.loads(file.read())

    # initiates discord bot which 
    bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

    # will start action when bot is running to test environment 1
    @bot.event
    async def on_ready():
        testEnv1 = bot.get_channel(content["TEST_ENV_1"])
        print("Hello there! I'm the job search bot :)")
        await testEnv1.send("Job Searching Bot is here!")

    # will send message to certain channel when command "item" typed followed by text
    @bot.command()
    async def item(ctx, itemInfo):
        testEnv2 = bot.get_channel(content["TEST_ENV_2"])
        await testEnv2.send(itemInfo) # send to different channel
        await ctx.send(itemInfo) # send to channel where command came from
    

    bot.run(content["BOT_TOKEN"])    
except FileNotFoundError:
   print("File not found.")