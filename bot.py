# to run file from command terminal (windows), type "py bot.py"
import discord
from discord.ext import commands

BOT_TOKEN = "MTIwMzUyMzk1ODk1NjA5NzUzNg.GlInOR.IwKUEPFL0z0xruOHgm-DeiTNT935RNsCWR6JbA"
TEST1_CHANNEL_ID = 1203872656743465070
TEST2_CHANNEL_ID = 1205087561073172490

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Hello there! I'm the job search bot :)")
    channel = bot.get_channel(TEST1_CHANNEL_ID)
    await channel.send("Job Searching Bot is here!")

@bot.command()
async def nj(ctx, jobPosting):
    test = bot.get_channel(TEST2_CHANNEL_ID)
    await test.send(jobPosting) # send to different channel
    # await ctx.send(jobPosting) # send to same channel

bot.run(BOT_TOKEN)