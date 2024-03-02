import discord

from discord.ui import View

from modals.admin import admin_modal

def admin_view(bot, main_category_id, tickets_category_id, ping_role_id, use_ping_role):
	class AdminView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label="Sell Account", style=discord.ButtonStyle.green, custom_id="sell_account")
		async def sell_account(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.send_modal(modal=admin_modal(bot, main_category_id, tickets_category_id, ping_role_id, use_ping_role))

	return AdminView()