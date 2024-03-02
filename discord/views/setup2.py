import discord

from discord.ui import View

from utils import discord as discord_utils
from modals.setup2 import setup_tickets_category_modal
from views.setup3 import setup_seller_role_view

def setup_tickets_category_view(bot, message, main_category_id):
	class SetupTicketsCategoryView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new category", style=discord.ButtonStyle.green)
		async def auto_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 2/6",
				content="Generating new category with name **\"Tickets\"**...",
				color_type="purple"
			), view=None)

			tickets_category = await interaction.guild.create_category("Tickets")
			tickets_category_id = tickets_category.id

			await tickets_category.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)

			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 3/6",
				content="Choose whether to automatically create a *\"Seller\"* role or use an existing one.",
				color_type="blue"
			), view=setup_seller_role_view(bot, message, main_category_id, tickets_category_id)) # go to setup 3

		@discord.ui.button(label=f"Use an existing category", style=discord.ButtonStyle.blurple)
		async def existing_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			return await interaction.response.send_modal(modal=setup_tickets_category_modal(bot, message, main_category_id)) # go to modal

	return SetupTicketsCategoryView()