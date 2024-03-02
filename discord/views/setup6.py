import discord

from discord.ui import View

import discord.utils as discord_utils
from modals.setup6 import setup_archive_category_modal, finish_setup

def setup_archive_category_view(bot: discord.Bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role):
	class SetupMainCategoryView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new category", style=discord.ButtonStyle.green)
		async def auto_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()


			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 6/6",
				content="Generating new category with name **\"Archive\"**...",
				color_type="purple"
			), view=None)

			archive_category = await interaction.guild.create_category("Archive")
			archive_category_id = archive_category.id

			await archive_category.set_permissions(interaction.guild.default_role, read_messages=False)

			return await finish_setup(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role, archive_category_id)

		@discord.ui.button(label=f"Use an existing category", style=discord.ButtonStyle.blurple)
		async def existing_category(self, button: discord.ui.Button, interaction: discord.Interaction):
			return await interaction.response.send_modal(modal=setup_archive_category_modal(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role))

	return SetupMainCategoryView()