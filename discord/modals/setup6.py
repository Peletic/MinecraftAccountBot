import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils
from views.admin import admin_view


def setup_archive_category_modal(bot: discord.Bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role):
	class SetupArchiveCategoryModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the category's ID below:", timeout=None)
			self.add_item(InputText(label="Category ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 6/6",
				content="Checking if everything is correct...",
				color_type="purple"
			), view=None)

			error_embed = await discord_utils.build_embed(
				title="Error",
				content="You must provide a **valid** category ID.",
				color_type="red"
			)

			if not self.children[0].value:
				return await message.edit(embed=error_embed)

			archive_category_id = int(self.children[0].value)

			try:
				archive_category = bot.get_channel(main_category_id)
			except:
				return await message.edit(embed=error_embed)

			if not archive_category:
				return await message.edit(embed=error_embed)


			return await finish_setup(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role, archive_category_id)



	return SetupArchiveCategoryModal()


async def finish_setup(bot: discord.Bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role, archive_category_id):
	await message.edit(embed=await discord_utils.build_embed(
		title="Finishing setup...",
		content="Creating final components and messages, please wait...",
		color_type="purple"
	), view=None)


	admin_channel = bot.get_channel(admin_channel_id)

	embed = await discord_utils.build_embed(
		title="Put an account for sale",
		content="Click the button below to create a new sale offer for an account.",
		color_type="blue",
		use_timestamp=False
	)

	admin_message = await admin_channel.send(embed=embed, view=admin_view(bot, main_category_id, tickets_category_id, ping_role_id, use_ping_role))

	admin_message_id = admin_message.id


	await message.edit(embed=await discord_utils.build_embed(
		title="Setup 6/6",
		content="Saving settings to database...",
		color_type="purple"
	), view=None)


	# database creation
	# todo error handling here, on both database calls
	try:
		database = bot.get_cog("Database")
		if not database.database:
			if await database.create_database() != 200:
				# todo pretty embed
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="Error while creating the database!",
					color_type="red"
				), view=None)
	except:
		return await message.edit(embed=await discord_utils.build_embed(
			title="Error",
			content="Error while creating the database!",
			color_type="red"
		), view=None)

	try:
		if await database.setup_database(main_category_id, admin_channel_id, admin_message_id, ping_role_id, use_ping_role, tickets_category_id, seller_role_id, vouch_channel_id, archive_category_id) != 200:
			# todo pretty embed
			return await message.edit(embed=await discord_utils.build_embed(
				title="Error",
				content="Error while setting up the database!",
				color_type="red"
			), view=None)
	except:
		return await message.edit(embed=await discord_utils.build_embed(
			title="Error",
			content="Error while creating the database!",
			color_type="red"
		), view=None)


	await message.edit(embed=await discord_utils.build_embed(
		title="Setup 6/6",
		content="Setup completed! Bot will now restart...",
		color_type="green"
	), view=None)

	exit(0)