import discord

from discord.ui import View

from utils import discord as discord_utils
from modals.setup4 import setup_vouch_channel_modal
from views.setup5 import setup_ping_role_view

def setup_vouch_channel_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id):
	class SetupVouchChannelView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new channel", style=discord.ButtonStyle.green)
		async def auto_channel(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 4/6",
				content="Generating new channel with name **\"Vouches\"**...",
				color_type="purple"
			), view=None)

			main_category = bot.get_channel(main_category_id)
			vouch_channel = await main_category.create_text_channel("vouches")
			vouch_channel_id = vouch_channel.id

			seller_role = interaction.guild.get_role(seller_role_id)

			# set permissions for the vouch channel
			await vouch_channel.set_permissions(seller_role, read_messages=True, send_messages=True)
			await vouch_channel.set_permissions(interaction.guild.default_role, read_messages=True, send_messages=False)

			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 5/6",
				content="Choose whether to automatically create a *\"New Accounts Ping\"* role, use an existing one or not create one at all.",
				color_type="blue"
			), view=setup_ping_role_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id))

		@discord.ui.button(label=f"Use an existing channel", style=discord.ButtonStyle.blurple)
		async def existing_channel(self, button: discord.ui.Button, interaction: discord.Interaction):
			return await interaction.response.send_modal(modal=setup_vouch_channel_modal(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id))

	return SetupVouchChannelView()