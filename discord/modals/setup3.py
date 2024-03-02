import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils

from views.setup4 import setup_vouch_channel_view

def setup_seller_role_modal(bot: discord.Bot, message, main_category_id, tickets_category_id):
	class SetupTicketsCategoryModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the role's ID below:", timeout=None)
			self.add_item(InputText(label="Role ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 3/6",
				content="Checking if everything is correct...",
				color_type="purple"
			), view=None)

			error_embed = await discord_utils.build_embed(
				title="Error",
				content="You must provide a **valid** role ID for a role in this server.",
				color_type="red"
			)

			if not self.children[0] or not self.children[0].value:
				return await message.edit(embed=error_embed)

			seller_role_id = int(self.children[0].value)

			try:
				seller_role = interaction.guild.get_role(seller_role_id)
			except:
				return await message.edit(embed=error_embed)

			if not seller_role:
				return await message.edit(embed=error_embed)


			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 3/6",
				content="Generating channel for sellers and admins to use for creating sales...",
				color_type="purple"
			))

			main_category = bot.get_channel(main_category_id)

			# setup the admin/seller only channel and its embed.
			admin_channel = await main_category.create_text_channel("admin")
			admin_channel_id = admin_channel.id

			await admin_channel.set_permissions(seller_role, read_messages=True)
			await admin_channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)


			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 4/5",
				content="Choose whether to automatically create a *\"Vouches\"* channel or use an existing one.",
				color_type="blue"
			), view=setup_vouch_channel_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id))



	return SetupTicketsCategoryModal()