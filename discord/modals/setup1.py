import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils

from views.setup2 import setup_tickets_category_view

def setup_main_category_modal(bot: discord.Bot, message):
	class SetupMainCategoryModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the category's ID below:", timeout=None)
			self.add_item(InputText(label="Category ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 1/6",
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

			main_category_id = int(self.children[0].value)

			try:
				main_category = bot.get_channel(main_category_id)
			except:
				return await message.edit(embed=error_embed)

			if not main_category:
				return await message.edit(embed=error_embed)


			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 2/6",
				content="Choose whether to automatically generate a *\"Tickets\"* category or use an existing one.",
				color_type="blue"
			), view=setup_tickets_category_view(bot, message, main_category_id)) # go to setup 2



	return SetupMainCategoryModal()