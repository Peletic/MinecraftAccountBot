import discord
import asyncio

from discord.ui import View
from utils import discord as discord_utils
from modals.account import account_modal

async def account_view(bot, str_price, account_id):
	database = bot.get_cog("Database")
	# todo add error handling for these db calls
	config, _ = await database.get_config()
	account, _ = await database.get_account(account_id)

	class AccountView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Buy for ${str_price}", style=discord.ButtonStyle.green, custom_id="buy_account")
		async def buy_account(self, button: discord.ui.Button, interaction: discord.Interaction):
			if interaction.user.id == int(account['seller_discord_id']):
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content="You can't buy your own account!",
					color_type="red"
				), ephemeral=True)

			await interaction.response.send_modal(modal=account_modal(bot, account_id, config, str_price))

		if config['use_ping_role']:
			@discord.ui.button(label="Toggle Ping Role", style=discord.ButtonStyle.blurple, custom_id="toggle_ping_role")
			async def toggle_ping_role(self, button: discord.ui.Button, interaction: discord.Interaction):
				await interaction.response.defer()
				try:
					role = interaction.guild.get_role(int(config['ping_role_id']))
					if role in interaction.user.roles:
						await interaction.user.remove_roles(role)
						await interaction.followup.send(embed=await discord_utils.build_embed(
							title="Success",
							content="You will no longer be pinged when a new account is listed!",
							color_type="green"
						), ephemeral=True)
					else:
						await interaction.user.add_roles(role)
						await interaction.followup.send(embed=await discord_utils.build_embed(
							title="Success",
							content=f"You have now been added to the role {role.mention} and will be pinged when a new account is listed!",
							color_type="green"
						), ephemeral=True)
				except:
					await interaction.followup.send(embed=await discord_utils.build_embed(
						title="Error",
						content="There was an error while toggling your ping role, please contact a staff member.",
						color_type="red"
					), ephemeral=True)

		# @discord.ui.button(label="Refresh", style=discord.ButtonStyle.blurple, custom_id="refresh_account")

		@discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete_account")
		async def delete_account(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			# check if user is not seller OR has admin perms
			if interaction.user.id != int(account['seller_discord_id']) and not interaction.user.guild_permissions.administrator:
				return await interaction.followup.send(embed=await discord_utils.build_embed(
					title="Error",
					content="You don't have permissions to delete this account sale.",
					color_type="red"
				), ephemeral=True)


			tickets, status = await database.get_tickets_for_account(account_id)

			if status != 200:
				return await interaction.followup.send(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while deleting this account sale, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			archive_category = interaction.guild.get_channel(int(config['archive_category_id']))

			for ticket in tickets:
				ticket_channel = interaction.guild.get_channel(int(ticket['channel_id']))
				buyer = interaction.guild.get_member(int(ticket['buyer_discord_id']))
				ticket_message = await ticket_channel.fetch_message(int(ticket['message_id']))
				if ticket_channel:
					await ticket_channel.set_permissions(buyer, read_messages=False, send_messages=False)
					await ticket_channel.edit(category=archive_category)
					await ticket_message.edit(view=None)

					await buyer.send(embed=await discord_utils.build_embed(
						title="Ticket Closed",
						content=f"The ticket you opened for the account #{account['id']} for ${account['price']} has been closed because the sell offer has been taken down by the seller or a staff member.",
						color_type="blue"
					))

			status = await database.delete_account(account_id)


			if status != 200:
				return await interaction.followup.send(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while deleting this account sale, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			await interaction.followup.send(embed=await discord_utils.build_embed(
				title="Success",
				content="This account sale has been deleted! This channel will be deleted in 15 seconds.",
				color_type="green"
			), ephemeral=False)

			# remove the view from the message
			await interaction.message.edit(view=None)

			await asyncio.sleep(15)

			await interaction.channel.delete()

	return AccountView()