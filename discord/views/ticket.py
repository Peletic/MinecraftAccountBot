import discord
import asyncio

from discord.ui import View
from utils import discord as discord_utils
from modals.vouch import vouch_modal

async def ticket_view(bot:discord.Bot, account_id, buyer_discord_id):
	database = bot.get_cog("Database")
	config, _ = await database.get_config()
	account, _ = await database.get_account(account_id)

	class TicketView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Close Ticket", style=discord.ButtonStyle.red)
		async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			buyer = bot.get_user(int(buyer_discord_id))

			delete_status = await database.delete_ticket(account_id, buyer_discord_id)

			if delete_status != 200:
				return await interaction.followup.send(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while closing the ticket, please contact a staff member.",
					color_type="red"
				), ephemeral=True)


			message = await interaction.followup.send(embed=await discord_utils.build_embed(
				title="Ticket Closed",
				content=f"The ticket has been closed by {interaction.user.mention}.",
				color_type="green"
			))

			await interaction.message.edit(view=None)

			await interaction.channel.set_permissions(buyer, send_messages=False, read_messages=False)

			await message.edit(view=await ticket_close_view(bot, account_id, buyer_discord_id, message, (int(account['seller_discord_id'])), interaction.message))



		@discord.ui.button(label=f"Mark as Sold", style=discord.ButtonStyle.green)
		async def mark_as_sold(self, button: discord.ui.Button, interaction: discord.Interaction):
			if interaction.user.id != int(account['seller_discord_id']):
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content=f"You are not the seller of this account, you cannot mark it as sold. If you believe this sale offer is no longer valid, please contact the account seller <@{account['seller_discord_id']}>",
					color_type="red"
				), ephemeral=True)

			await interaction.response.defer()

			message = await interaction.followup.send(embed=await discord_utils.build_embed(
				title="Marking as Sold...",
				content=f"Please wait while we mark the account as sold.",
				color_type="purple"
			))

			tickets, status = await database.get_tickets_for_account(account_id)

			if status != 200:
				return message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while deleting this account sale, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			archive_category = interaction.guild.get_channel(int(config['archive_category_id']))

			archived_ticket_ids = []

			for ticket in tickets:
				# if the ticket is this ticket, skip it
				if int(ticket['channel_id']) == interaction.channel.id: continue

				ticket_channel = interaction.guild.get_channel(int(ticket['channel_id']))
				buyer = interaction.guild.get_member(int(ticket['buyer_discord_id']))
				ticket_message = await ticket_channel.fetch_message(int(ticket['message_id']))
				if ticket_channel:
					await ticket_channel.set_permissions(buyer, read_messages=False, send_messages=False)
					await ticket_channel.edit(category=archive_category)
					await ticket_message.edit(view=None)
					archived_ticket_ids.append(int(ticket['channel_id']))

					await buyer.send(embed=await discord_utils.build_embed(
						title="Ticket Closed",
						content=f"The ticket you opened for the account #{account['id']} for ${account['price']} has been closed because the sell offer has been taken down by the seller or a staff member.",
						color_type="blue"
					))

			status = await database.sell_account(account_id)


			if status != 200:
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while deleting this account sale, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			# delete the account channel
			account_channel = interaction.guild.get_channel(int(account['channel_id']))
			await account_channel.delete()


			# remove the buyer's permission to talk in the channel
			buyer = bot.get_user(int(buyer_discord_id))

			close_message =await message.edit(embed=await discord_utils.build_embed(
				title="Account Sold!",
				content=f"This account has been sold to {buyer.mention} by {interaction.user.mention}!",
				color_type="green"
			))

			await interaction.channel.set_permissions(buyer, send_messages=False, read_messages=False)

			await interaction.message.edit(view=None)

			await close_message.edit(view=await ticket_close_view(bot, account_id, buyer_discord_id, message, (int(account['seller_discord_id'])), interaction.message, no_reopen=True))

			# sends the vouch prompt to the buyer's dm
			vouch_message = await buyer.send(embed=await discord_utils.build_embed(
				title="Successful Purchase!",
				content=f"Congratulations on your purchase of account #{account_id}! Please remember to vouch the seller {interaction.user.mention} by clicking the button below.",
				color_type="blue"
			))

			await vouch_message.edit(view=await vouch_view(bot, vouch_message, (int(account['seller_discord_id']))))





	return TicketView()


async def ticket_close_view(bot: discord.Bot, account_id, buyer_discord_id, message, seller_discord_id, old_message, no_reopen=False):
	database = bot.get_cog("Database")
	config, _ = await database.get_config()

	class TicketCloseView(View):
		if not no_reopen:
			@discord.ui.button(label=f"Reopen Ticket", style=discord.ButtonStyle.green)
			async def reopen_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
				if not await discord_utils.is_admin(interaction) and interaction.user.id != seller_discord_id:
					return await interaction.response.send_message(embed=await discord_utils.build_embed(
						title="Error",
						content="You do not have permission to use this button.",
						color_type="red"
					), ephemeral=True)

				await interaction.response.defer()

				ticket_status = await database.make_ticket_channel(interaction.channel.id, old_message.id, account_id, buyer_discord_id)

				if ticket_status != 200:
					return await interaction.followup.send(embed=await discord_utils.build_embed(
						title="Error",
						content="There was an error while reopening the ticket, please contact a staff member.",
						color_type="red"
					), ephemeral=True)

				buyer = bot.get_user(int(buyer_discord_id))

				await interaction.channel.set_permissions(buyer, send_messages=True, read_messages=True)

				await message.edit(embed=await discord_utils.build_embed(
					title="Ticket Reopened",
					content=f"{buyer.mention}, your ticket has been reopened by {interaction.user.mention}.",
					color_type="green"
				), view=None)

				# readd the view in the old message
				await old_message.edit(view=await ticket_view(bot, account_id, buyer_discord_id))

		@discord.ui.button(label=f"Archive Ticket", style=discord.ButtonStyle.grey)
		async def archive_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
			if not await discord_utils.is_admin(interaction) and interaction.user.id != seller_discord_id:
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content="You do not have permission to use this button.",
					color_type="red"
				), ephemeral=True)


			await message.edit(embed=await discord_utils.build_embed(
				title="Ticket Archived",
				content=f"The ticket has been archived by {interaction.user.mention} and will be moved to the archive category in 15 seconds.",
				color_type="green"
			), view=None)

			await asyncio.sleep(15)

			await interaction.channel.edit(category=interaction.guild.get_channel(int(config['archive_category_id'])))

			await message.edit(embed=await discord_utils.build_embed(
				title="Ticket Archived",
				content=f"This ticket was archived by {interaction.user.mention}",
				color_type="green"
			), view=None)

		@discord.ui.button(label=f"Delete Ticket", style=discord.ButtonStyle.red)
		async def delete_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
			if not await discord_utils.is_admin(interaction) and interaction.user.id != seller_discord_id:
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content="You do not have permission to use this button.",
					color_type="red"
				), ephemeral=True)

			await message.edit(embed=await discord_utils.build_embed(
				title="Ticket Deleted",
				content=f"The ticket has been set to be deleted by {interaction.user.mention}. This channel will be deleted in 15 seconds.",
				color_type="green"
			), view=None)


			await asyncio.sleep(15)

			await interaction.channel.delete()


	return TicketCloseView()


async def vouch_view(bot: discord.Bot, message, seller_discord_id):
	class VouchView(View):
		def __init__(self):
			super().__init__(timeout=None)

		@discord.ui.button(label=f"Vouch", style=discord.ButtonStyle.green)
		async def vouch(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.send_modal(await vouch_modal(bot, message, seller_discord_id, False))

		@discord.ui.button(label="Vouch anonymously", style=discord.ButtonStyle.grey)
		async def vouch_anonymously(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.send_modal(await vouch_modal(bot, message, seller_discord_id, True))

		@discord.ui.button(label=f"Cancel", style=discord.ButtonStyle.red)
		async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
			await interaction.response.defer()

			await message.edit(embed=await discord_utils.build_embed(
				title="Vouch cancelled",
				content=f"We understand that you may not want to vouch. Thank you for doing business with us and have a nice day!",
				color_type="red"
			), view=None)

	return VouchView()