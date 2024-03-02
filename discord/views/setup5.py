import discord

from discord.ui import View

from utils import discord as discord_utils

from modals.setup5 import setup_ping_role_modal
from views.setup6 import setup_archive_category_view

def setup_ping_role_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id):
	class SetupSellerRoleView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new role", style=discord.ButtonStyle.green)
		async def auto_role(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 5/5",
				content="Generating new role with name **\"New Accounts Ping\"**...",
				color_type="purple"
			), view=None)

			# todo try catch this
			ping_role = await interaction.guild.create_role(name="New Accounts Ping")
			ping_role_id = ping_role.id
			use_ping_role = True

			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 6/6",
				content="Choose whether to automatically create a *\"Archive\"* category or use an existing one.",
				color_type="blue"
			), view=setup_archive_category_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role)) # go to setup 6

		@discord.ui.button(label=f"Use an existing role", style=discord.ButtonStyle.blurple)
		async def existing_role(self, button: discord.ui.Button, interaction: discord.Interaction):
			return await interaction.response.send_modal(modal=setup_ping_role_modal
(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id))

		@discord.ui.button(label=f"Don't create a role", style=discord.ButtonStyle.red, custom_id="dont_create_role")
		async def no_role(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			ping_role_id = None
			use_ping_role = False

			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 6/6",
				content="Choose whether to automatically create a *\"Archive\"* category or use an existing one.",
				color_type="blue"
			), view=setup_archive_category_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role)) # go to setup 6

	return SetupSellerRoleView()