import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils
from views.setup6 import setup_archive_category_view


def setup_ping_role_modal(bot: discord.Bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id):
	class SetupPingRoleModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the role's ID below:", timeout=None)
			self.add_item(InputText(label="Role ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 5/6",
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

			ping_role_id = int(self.children[0].value)
			use_ping_role = True

			try:
				ping_role = interaction.guild.get_role(seller_role_id)
			except:
				return await message.edit(embed=error_embed)

			if not ping_role:
				return await message.edit(embed=error_embed)


			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 6/6",
				content="Choose whether to automatically create a *\"Archive\"* category or use an existing one.",
				color_type="blue"
			), view=setup_archive_category_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id, ping_role_id, use_ping_role)) # go to setup 6


	return SetupPingRoleModal()