import discord
from discord.ext import tasks, commands
import datetime
import asyncio
from cockroach import Database
from dotenv import load_dotenv
import typing
import os
from discord import app_commands

class FoodExpirationBot:
    def __init__(self) -> None:
        # Initialize bot and database
        self.bot = commands.Bot(command_prefix="", intents=discord.Intents.default())
        self.db = Database()

        # Set up the command tree (no need for this because structure already exists)
        self.bot.tree = app_commands.CommandTree(self.bot)

        # Register bot events and commands
        self.setup()

    def setup(self):
        # Register events
        self.bot.event(self.on_ready)

    async def on_ready(self):
        # Register commands
        self.bot.tree.command(name="item", description="Add a TEST new food item with an expiration date")(self.add_item)
        self.bot.tree.command(name="list", description="List all TEST items in your account")(self.list_items)
        self.bot.tree.command(name="delete", description="Delete an TEST item from your account")(self.delete_item)

        discordGuild = discord.Object(id=int(os.getenv("SERVER_GUILD")))
        self.bot.tree.clear_commands(guild=discordGuild)
        await self.bot.tree.sync(guild=discordGuild)
        foodChannel = self.bot.get_channel(int(os.getenv("FOOD_CHANNEL")))
        await foodChannel.send("Food Expiration Bot is here!")

    async def add_item(self, interaction: discord.Interaction, item_name: str, expiration_date: typing.Optional[str] = None):
        username = interaction.user.mention
        itemInfo = [item_name, expiration_date]
        inserted = self.db.insertItem(username, itemInfo)
        if inserted:
            await interaction.response.send_message("Item inserted!")
        else:
            await interaction.response.send_message("Unable to add item. Please make sure expiration date is valid entry.")

    async def list_items(self, interaction: discord.Interaction):
        username = interaction.user.mention
        items = self.db.listItems(username)
        if len(items) == 0:
            await interaction.response.send_message("There are no items under your account")
        else:
            itemList = "You have the following items:\n"
            for item in items:
                itemList += f"- {item[0]} ({item[1].month}/{item[1].day}/{item[1].year})\n"
            await interaction.response.send_message(itemList)

    async def delete_item(self, interaction: discord.Interaction, item_name: str):
        username = interaction.user.mention
        deleted = self.db.deleteItem(username, item_name)
        if deleted != 0:
            await interaction.response.send_message(f"{item_name} has been removed from your account!")
        else:
            await interaction.response.send_message("Item does not exist under your account")

    @tasks.loop(hours=24)
    async def check_expirations(self):
        now = datetime.datetime.now()
        scheduledTime = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now > scheduledTime:
            scheduledTime += datetime.timedelta(days=1)

        await asyncio.sleep((scheduledTime - now).total_seconds())

        today = datetime.date.today()
        expiresToday = self.db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for user in expiresToday:
            message = f"{user} The following items expire today:\n"
            for item in expiresToday[user]:
                message += f"- {item}\n"
            await self.expirationChannel.send(message)

        self.db.deleteExpiredItems(datetime.datetime(today.year, today.month, today.day))

        today += datetime.timedelta(days=2)
        expires_later = self.db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for user in expires_later:
            message = f"{user} The following items expire in two days:\n"
            for item in expires_later[user]:
                message += f"- {item}\n"
            expirationChannel = self.bot.get_channel(int(os.getenv("EXPIRATION_CHANNEL")))
            await expirationChannel.send(message)

    def run(self):
        if os.getenv("BOT_TOKEN"):
            self.bot.run(os.getenv("BOT_TOKEN"))
            
        # Start the expiration check loop
        if not self.check_expirations.is_running():
            self.check_expirations.start()


if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    bot = FoodExpirationBot()
    bot.run()