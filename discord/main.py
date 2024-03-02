import json
import discord
import asyncio

# check for the config.json file, if it doesn't exist, create it
try:
	with open('./config.json') as f:
		config = json.load(f)
except FileNotFoundError:
	# make a config json with DISCORD_BOT_TOKEN and HYPIXEL_API_KEY
	with open('./config.json', 'w') as f:
		json.dump({
			"DISCORD_BOT_TOKEN": "",
			"HYPIXEL_API_KEY": ""
		}, f, indent=4)

	# print that the config file has been created and must be filled
	print("Config file created, please fill it with the required information and restart the bot.")
	exit()

from database.sqlite import Database
from commands.setup import Setup
from modules.refresh import refresh


BOT_TOKEN = config['DISCORD_BOT_TOKEN'] if 'DISCORD_BOT_TOKEN' in config else None
API_KEY = config['HYPIXEL_API_KEY'] if 'HYPIXEL_API_KEY' in config else None


if BOT_TOKEN is None or BOT_TOKEN == "": raise Exception('DISCORD_BOT_TOKEN is not defined in config.json')
if "HYPIXEL_API_KEY" not in config or config["HYPIXEL_API_KEY"] is None or config["HYPIXEL_API_KEY"] == "": raise Exception('HYPIXEL_API_KEY is not defined in config.json')

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

bot.add_cog(Database(bot))
database = bot.get_cog("Database")

if not database.database:
	print("Bot is in setup mode, please run the setup command to continue.")
	bot.add_cog(Setup(bot))
else:
	# todo implement message refresh after bot restart (to fix broken buttons and stuff)
	config, status_code = asyncio.run(database.get_config())

	if status_code != 200:
		raise Exception(f"Error while fetching config: {status_code}")

	accounts, status_code = asyncio.run(database.get_accounts())

	if status_code != 200:
		raise Exception(f"Error while fetching accounts: {status_code}")

	tickets, status_code = asyncio.run(database.get_tickets())

	if status_code != 200:
		raise Exception(f"Error while fetching tickets: {status_code}")

	bot.loop.create_task(refresh(bot, accounts, tickets, config))

	# asyncio.run(refresh(bot, [], [], config))


bot.run(BOT_TOKEN)
