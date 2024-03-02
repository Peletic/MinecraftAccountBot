import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils

from views.setup5 import setup_ping_role_view

def setup_vouch_channel_modal(bot: discord.Bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id):
	class SetupVouchChannelModal(Modal):
		def __init__(self):
			super().__init__(title="Insert the channel's ID below:", timeout=None)
			self.add_item(InputText(label="Channel ID"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 4/6",
				content="Checking if everything is correct...",
				color_type="purple"
			), view=None)

			error_embed = await discord_utils.build_embed(
				title="Error",
				content="You must provide a **valid** channel ID.",
				color_type="red"
			)

			if not self.children[0].value:
				return await message.edit(embed=error_embed)

			vouch_channel_id = int(self.children[0].value)

			try:
				vouch_channel = bot.get_channel(vouch_channel_id)
			except:
				return await message.edit(embed=error_embed)

			if not vouch_channel:
				return await message.edit(embed=error_embed)


			return await message.edit(embed=await discord_utils.build_embed(
				title="Setup 5/6",
				content="Choose whether to automatically create a *\"New Accounts Ping\"* role, use an existing one or not create one at all.",
				color_type="blue"
			), view=setup_ping_role_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id, vouch_channel_id))



	return SetupVouchChannelModal()