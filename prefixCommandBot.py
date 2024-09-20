# to run file from command terminal (windows), type "py bot.py"
# to run file from command terminal (mac), type "python3 bot.py"
# to install libraries, use command "py -m pip install item_name"

import discord
from discord.ext import tasks, commands
import datetime
from cockroach import Database
from dotenv import load_dotenv
import os
import asyncio

# retrieves secret keys from .env
load_dotenv()
# mongodb class
db = Database()

# initiates discord bot which 
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# will start action when bot is running
@bot.event
async def on_ready():
    foodChannel = bot.get_channel(int(os.getenv("FOOD_CHANNEL")))
    # await bot.tree.sync()
    await foodChannel.send("Food Expiration Bot is here!")
    check_expirations.start()

# process data for new food item and expiration date
@bot.command()
async def item(ctx, *args):
    username = ctx.author.mention
    itemInfo = [words for words in args]
    inserted = db.insertItem(username, itemInfo)
    if inserted:
        await ctx.send("Item inserted!")
    else:
        await ctx.send("Unable to add item")

# lists all the current items you have stored in your account
@bot.command()
async def list(ctx):
    username = ctx.author.mention
    items = db.listItems(username)
    if len(items) == 0:
        await ctx.send("There are no items under your account")
    else:
        itemList = "You have the following items:\n"
        for item in items:
            itemList += f"- {item[0]} ({item[1].month}/{item[1].day})\n"
        await ctx.send(itemList)

# deletes an item in your account
@bot.command()
async def delete(ctx, *args):
    username = ctx.author.mention
    item = " ".join([words for words in args])
    deleted = db.deleteItem(username, item)
    if deleted != 0:
        await ctx.send(f"{item} has been removed from your account!")
    else:
        await ctx.send("Item does not exist under your account")


# loop checks for expiring items and deletes expired items
@tasks.loop(hours=24)
async def check_expirations():
    # initializes loop for 9am everyday
    now = datetime.datetime.now()
    scheduledTime = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now > scheduledTime:
        scheduledTime += datetime.timedelta(days=1)

    # won't start rest of code until scheduled time comes
    await asyncio.sleep((scheduledTime - now).total_seconds())

    expirationChannel = bot.get_channel(int(os.getenv("EXPIRATION_CHANNEL")))
    # expirationChannel = bot.get_channel(content["TEST_ENV_2"])

    # run code to check for any expiring items today
    today = datetime.date.today()
    expiresToday = db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
    for user in expiresToday:
        message = f"{user} The following items expire today:\n"
        for item in expiresToday[user]:
            message += f"- {item}\n"
        await expirationChannel.send(message)

    # delete any old items that have already expired
    db.deleteExpiredItems(datetime.datetime(today.year, today.month, today.day))

    # run code to check for any expiring items within the next two days
    today += datetime.timedelta(days=2)
    expiresLater = db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
    for user in expiresLater:
        message = f"{user} The following items expire in two days:\n"
        for item in expiresLater[user]:
            message += f"- {item}\n"
        await expirationChannel.send(message)

bot.run(os.getenv("BOT_TOKEN"))    