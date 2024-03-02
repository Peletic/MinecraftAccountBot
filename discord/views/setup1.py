import discord

from discord.ui import View

from utils import discord as discord_utils
from modals.setup1 import setup_main_category_modal
from views.setup2 import setup_tickets_category_view

def setup_main_category(bot, message):
	class SetupMainCategoryView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new category", style=discord.ButtonStyle.green)
		async def auto_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()


			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 1/6",
				content="Generating new category with name **\"Accounts\"**...",
				color_type="purple"
			), view=None)

			main_category = await interaction.guild.create_category("Accounts")
			main_category_id = main_category.id

			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 2/6",
				content="Choose whether to automatically generate a *\"Tickets\"* category or use an existing one.",
				color_type="blue"
			), view=setup_tickets_category_view(bot, message, main_category_id)) # go to setup 2

		@discord.ui.button(label=f"Use an existing category", style=discord.ButtonStyle.blurple)
		async def existing_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			# go to modal
			return await interaction.response.send_modal(modal=setup_main_category_modal(bot, message))

	return SetupMainCategoryView()