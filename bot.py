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
        # foodChannel = bot.get_channel(content["FOOD_CHANNEL"])
        foodChannel = bot.get_channel(content["TEST_ENV_1"])
        await foodChannel.send("Food Expiration Bot is here!")
        check_expirations.start()

    # process data for new food item and expiration date
    @bot.command()
    async def item(ctx, *args):
        username = ctx.author.mention
        itemInfo = list(args)
        inserted = db.insertItem(username, itemInfo)
        if inserted:
            await ctx.send(f"{username} Item inserted!") # send to channel where command came from
    
    @tasks.loop(hours=24)
    async def check_expirations():
        # initializes loop for 9am everyday
        now = datetime.datetime.now()
        scheduledTime = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now > scheduledTime:
            scheduledTime += datetime.timedelta(days=1)

        # won't start rest of code until scheduled time comes
        await asyncio.sleep((scheduledTime - now).total_seconds())

        # expirationChannel = bot.get_channel(content["EXPIRATION_CHANNEL"])
        expirationChannel = bot.get_channel(content["TEST_ENV_2"])

        # run code to check for any expiring items today
        today = datetime.date.today()
        expiresToday = db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for item in expiresToday:
            await expirationChannel.send(f"{item[0]} {item[1]} expires today!")

        # delete any old items that have already expired
        db.deleteOldExpirations(datetime.datetime(today.year, today.month, today.day))

        # run code to check for any expiring items within the next two days
        today += datetime.timedelta(days=2)
        expiresLater = db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for item in expiresLater:
            await expirationChannel.send(f"{item[0]} {item[1]} expires in two days!")

    bot.run(content["BOT_TOKEN"])    

except FileNotFoundError:
   print("File not found.")