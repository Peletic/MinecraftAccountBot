from utils import discord as discord_utils
from discord.ext import commands
import discord

from views.admin import admin_view
from utils import discord as discord_utils
from views.setup1 import setup_main_category


class Setup(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot

	@commands.slash_command(name="setup", description="Setup the bot")
	async def setup(self, interaction:discord.Interaction):
		# main_category_id (category where the sold accounts and account for sale will be)
		# admin_channel_id (category where there will be the message with buttons to create a sale and maybe other stuff related to managing the bot) -> this is in the main_category
		# admin_message_id (message with buttons to create a sale) -> this is in the admin_channel
		# ping_role_id (role that will be pinged when a new account is added, see chimera's @pinga) -> option to manually add a existing role by id, automatically create a new role (that can be later edited) or not use a role at all, see next option
		# use_ping_role (boolean, if true ping_role_id will be used, if false the bot will ping @everyone) -> if no role_id is provided, this will be set to false
		# tickets_category_id (category where the tickets will be created) -> tickets are automatically created when the buyer clicks the buy button, the ticket will be deleted when the buyer clicks the close button. -> different category from the main_category

		await interaction.response.defer()

		message = await interaction.followup.send(embed=await discord_utils.build_embed(
			title="Setup 1/6",
			content="Choose wether to automatically generate a *\"Accounts\"* category or use an existing one.",
			color_type="blue"
		))

		return await message.edit(view=setup_main_category(self.bot, message))


async def old_setup(interaction, self):
	# start by creating the main category
	main_category = await interaction.guild.create_category("Accounts")
	main_category_id = main_category.id
	# create the tickets category
	tickets_category = await interaction.guild.create_category("Tickets")
	tickets_category_id = tickets_category.id


	# create the admin channel
	admin_channel = await main_category.create_text_channel("admin")
	admin_channel_id = admin_channel.id

	# create the message with buttons
	embed = await discord_utils.build_embed(title="Admin", content="Click the button below to create a new account for sale", color_type="green")
	message = await admin_channel.send(embed=embed, view=admin_view(self.bot, main_category_id, tickets_category_id, None, False))
	admin_message_id = message.id

	# todo query for ping role, add a modal maybe? for now we keep it simple

	ping_role = await interaction.guild.create_role(name="New Account Ping")

	# database creation
	# todo error handling here, on both database calls
	database = self.bot.get_cog("Database")
	if not database.database:
		if await database.create_database() != 200:
			# todo pretty embed
			return await interaction.response.send_message("Error while creating the database!", ephemeral=True)

	if await database.setup_database(main_category_id, admin_channel_id, admin_message_id, ping_role.id, False, tickets_category_id) != 200:
		# todo pretty embed
		return await interaction.response.send_message("Error while setting up the database!", ephemeral=True)

	await interaction.response.send_message("Setup complete!", ephemeral=True)

	# force the discord bot to restart by exiting the current process and abusing docker's restart policy
	# todo this is a temporary solution, find a better way to do this
	# exit(0)