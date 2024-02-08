# to run file from command terminal (windows), type "py bot.py"
import discord
from discord.ext import commands
import json

try:
    with open('secret.json') as file:
        content = json.loads(file.read())
    
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print("Hello there! I'm the job search bot :)")
        channel = bot.get_channel(content["TEST1_CHANNEL_ID"])
        await channel.send("Job Searching Bot is here!")

    @bot.command()
    async def nj(ctx, jobPosting):
        test = bot.get_channel(content["TEST2_CHANNEL_ID"])
        await test.send(jobPosting) # send to different channel
        # await ctx.send(jobPosting) # send to same channel

    bot.run(content["BOT_TOKEN"])
    
except FileNotFoundError:
   print("File not found.")

