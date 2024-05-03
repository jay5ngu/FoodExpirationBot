# to run file from command terminal (windows), type "py bot.py"
# to run file from command terminal (mac), type "python3 bot.py"
import discord
from discord.ext import tasks, commands
import datetime
import json
import re

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
    async def item(ctx, *args):
        itemInfo = list(args)
        # format in mm/dd/yy
        pattern = r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{2}$"
        # format in mm/dd
        pattern_short = r"^(0?[1-9]|1[0-2])/\d{2}$"

        # if last value is expiration date in the format m/d/yy
        if re.match(pattern, itemInfo[-1]):
            expirationDate = datetime.datetime.strptime(itemInfo[-1], "%m/%d/%y").date()
            food = " ".join(itemInfo[0:len(itemInfo)-1])
        # if last value is expiration date in the format m/d
        elif re.match(pattern_short, itemInfo[-1]):
            date = itemInfo[-1] + "/" + str(datetime.datetime.now().year)
            expirationDate = datetime.datetime.strptime(date, "%m/%d/%Y").date()
            food = " ".join(itemInfo[0:len(itemInfo)-1])
        # if no expiration date listed
        else:
            expirationDate = datetime.date.today() + datetime.timedelta(days=2)  # Otherwise, default two days till expire
            food = " ".join(itemInfo)
        
        print("Expiration Date:", expirationDate)
        print("Item:", food)

        testEnv2 = bot.get_channel(content["TEST_ENV_2"])
        await testEnv2.send(itemInfo) # send to different channel
        await ctx.send(itemInfo) # send to channel where command came from
    

    bot.run(content["BOT_TOKEN"])    
except FileNotFoundError:
   print("File not found.")