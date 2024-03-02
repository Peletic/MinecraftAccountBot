import discord

from discord.ui import View

from utils import discord as discord_utils
from views.setup4 import setup_vouch_channel_view
from modals.setup3 import setup_seller_role_modal


def setup_seller_role_view(bot, message, main_category_id, tickets_category_id):
	class SetupSellerRoleView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Create a new role", style=discord.ButtonStyle.green)
		async def auto_role(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Setup 3/6",
				content="Generating new role with name **\"Seller\"**...",
				color_type="purple"
			), view=None)

			# todo try catch this
			seller_role = await interaction.guild.create_role(name="Seller")
			seller_role_id = seller_role.id

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
				title="Setup 4/6",
				content="Choose whether to automatically create a *\"Vouches\"* channel or use an existing one.",
				color_type="blue"
			), view=setup_vouch_channel_view(bot, message, main_category_id, tickets_category_id, seller_role_id, admin_channel_id)) # go to setup 4

		@discord.ui.button(label=f"Use an existing role", style=discord.ButtonStyle.blurple)
		async def existing_role(self, button: discord.ui.Button, interaction: discord.Interaction):
			return await interaction.response.send_modal(modal=setup_seller_role_modal(bot, message, main_category_id, tickets_category_id))

	return SetupSellerRoleView()