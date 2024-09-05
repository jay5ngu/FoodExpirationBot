import discord
from discord.ext import tasks, commands
import datetime
import json
import asyncio
from cockroach import Database
# from discord import app_commands
# from mongo import Database

class FoodExpirationBot:
    def __init__(self) -> None:
        self.content = self.load_secrets()        
        if not self.content:
            print("Secret file not found or could not be loaded. Exiting...")
            return

        # Initialize bot and database
        self.bot = commands.Bot(command_prefix="", intents=discord.Intents.default())
        self.db = Database()

        # Set up the command tree (no need for this because structure already exists)
        # self.bot.tree = app_commands.CommandTree(self.bot)

        # Register bot events and commands
        self.setup()

    def load_secrets(self):
        try:
            with open('secret.json') as file:
                return json.loads(file.read())
        except FileNotFoundError:
            print("File not found.")
            return None

    def setup(self):
        # Register events
        self.bot.event(self.on_ready)

        # Register commands
        self.bot.tree.command(name="item", description="Add a new food item with an expiration date")(self.add_item)
        self.bot.tree.command(name="list", description="List all items in your account")(self.list_items)
        self.bot.tree.command(name="delete", description="Delete an item from your account")(self.delete_item)

    async def on_ready(self):
        food_channel = self.bot.get_channel(self.content["FOOD_CHANNEL"])
        await self.bot.tree.sync(guild=discord.Object(id=self.content["SERVER_GUILD"]))
        await food_channel.send("Food Expiration Bot is here!")

    async def add_item(self, interaction: discord.Interaction, item_name: str, expiration_date: str = None):
        username = interaction.user.mention
        item_info = [item_name, expiration_date]
        inserted = self.db.insertItem(username, item_info)
        if inserted:
            await interaction.response.send_message("Item inserted!")
        else:
            await interaction.response.send_message("Unable to add item")

    async def list_items(self, interaction: discord.Interaction):
        username = interaction.user.mention
        items = self.db.listItems(username)
        if len(items) == 0:
            await interaction.response.send_message("There are no items under your account")
        else:
            item_list = "You have the following items:\n"
            for item in items:
                item_list += f"- {item[0]} ({item[1].month}/{item[1].day}/{item[1].year})\n"
            await interaction.response.send_message(item_list)

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
        scheduled_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now > scheduled_time:
            scheduled_time += datetime.timedelta(days=1)

        await asyncio.sleep((scheduled_time - now).total_seconds())

        expiration_channel = self.bot.get_channel(self.content["EXPIRATION_CHANNEL"])

        today = datetime.date.today()
        expires_today = self.db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for user in expires_today:
            message = f"{user} The following items expire today:\n"
            for item in expires_today[user]:
                message += f"- {item}\n"
            await expiration_channel.send(message)

        self.db.deleteExpiredItems(datetime.datetime(today.year, today.month, today.day))

        today += datetime.timedelta(days=2)
        expires_later = self.db.checkExpiration(datetime.datetime(today.year, today.month, today.day))
        for user in expires_later:
            message = f"{user} The following items expire in two days:\n"
            for item in expires_later[user]:
                message += f"- {item}\n"
            await expiration_channel.send(message)

    def run(self):
        if self.content:
            self.bot.run(self.content["BOT_TOKEN"])
            
        # Start the expiration check loop
        if not self.check_expirations.is_running():
            self.check_expirations.start()


if __name__ == "__main__":
    bot = FoodExpirationBot()
    bot.run()