import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils

from views.setup3 import setup_seller_role_view

def setup_tickets_category_modal(bot: discord.Bot, message, main_category_id):
	class SetupTicketsCategoryModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the category's ID below:", timeout=None)
			self.add_item(InputText(label="Category ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 2/6",
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

			tickets_category_id = int(self.children[0].value)

			try:
				tickets_category = bot.get_channel(tickets_category_id)
			except:
				return await message.edit(embed=error_embed)

			if not tickets_category:
				return await message.edit(embed=error_embed)


			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 3/6",
				content="Choose whether to automatically create a *\"Seller\"* role or use an existing one.",
				color_type="blue"
			), view=setup_seller_role_view(bot, message, main_category_id, tickets_category_id)) # go to setup 3



	return SetupTicketsCategoryModal()