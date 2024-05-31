# to run file from command terminal (windows), type "py bot.py"
# to run file from command terminal (mac), type "python3 bot.py"
# to install libraries, use command "py -m pip install item_name"

import discord
from discord.ext import tasks, commands
import datetime
import json
from mongo import Database
import asyncio

# contains secret keys
content = None
# mongodb class
db = Database()

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
        await testEnv1.send("Food Expiration Bot is here!")
        send_daily_message.start()

    # process data for new food item and expiration date
    @bot.command()
    async def item(ctx, *args):
        itemInfo = list(args)
        inserted = db.insertItem(itemInfo)
        if inserted:
            testEnv2 = bot.get_channel(content["TEST_ENV_2"])
            await testEnv2.send("Item inserted!") # send to different channel
            # await ctx.send(itemInfo) # send to channel where command came from
    
    @tasks.loop(hours=24)
    async def send_daily_message():
        now = datetime.datetime.now()
        scheduledTime = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now > scheduledTime:
            scheduledTime += datetime.timedelta(days=1)
        
        await asyncio.sleep((scheduledTime - now).total_seconds())

        testEnv1 = bot.get_channel(content["TEST_ENV_1"])
        await testEnv1.send("Good morning! It's 6 AM!")

    bot.run(content["BOT_TOKEN"])    

except FileNotFoundError:
   print("File not found.")