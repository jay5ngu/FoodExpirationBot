# to run file from command terminal (windows), type "py bot.py"
import discord
from discord.ext import tasks, commands
import datetime
import json

content = None
utc = datetime.timezone.utc
times = [
    datetime.time(hour=6, minute=56, tzinfo=utc),
    datetime.time(hour=12, minute=30, tzinfo=utc),
    datetime.time(hour=18, minute=56, second=30, tzinfo=utc)
]

try:
    with open('secret.json') as file:
        content = json.loads(file.read())

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @tasks.loop(hours=6, minutes=58)
    async def my_task():
        print("My task is running!")
        test = bot.get_channel(content["TEST2_CHANNEL_ID"])
        await test.send("Task works!") # send to different channel

    @bot.event
    async def on_ready():
        print("Hello there! I'm the job search bot :)")
        channel = bot.get_channel(content["TEST1_CHANNEL_ID"])
        await channel.send("Job Searching Bot is here!")
        my_task.start()

    @bot.command()
    async def nj(ctx, jobPosting):
        test = bot.get_channel(content["TEST2_CHANNEL_ID"])
        await test.send(jobPosting) # send to different channel
        # await ctx.send(jobPosting) # send to same channel
    
    @bot.command()
    async def end(ctx):
        my_task.cancel()

    bot.run(content["BOT_TOKEN"])    
except FileNotFoundError:
   print("File not found.")