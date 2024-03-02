import discord

from discord import Bot

from views.admin import admin_view
from views.account import account_view
from views.ticket import ticket_view
from utils import discord as discord_utils

async def refresh(bot: Bot, accounts, tickets, config):
	await bot.wait_until_ready()

	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tickets | by @r3dlust"))

	database = bot.get_cog("Database")

	accounts_to_refresh = 0

	accounts_to_refresh = sum(1 for account in accounts if account['status'] == "FOR_SALE")

	print(f"Refreshing {accounts_to_refresh} account{'' if accounts_to_refresh == 1 and accounts_to_refresh != 0 else 's'} (for sale), {len(tickets)} open ticket{'' if len(tickets) == 1 and len(tickets) != 0 else 's'} and the admin message...")

	status_code = await refresh_admin_message(bot, config)

	if status_code != 200:
		print(f"Error while refreshing admin message")
		return status_code

	for account in accounts:
		if account['status'] != "FOR_SALE": continue


		status_code = await refresh_account(bot, account)

		if status_code == 404:
			print(f"Account {account['id']} MIA or incomplete, setting state to MISSING and deleting all of its tickets...")

			tickets, status = await database.get_tickets_for_account(account['id'])

			if status != 200:
				print(f"Error while getting tickets for account {account['id']}")
				return 500

			archive_category = bot.get_channel(int(config['archive_category_id']))
			all_members = bot.get_all_members()

			for ticket in tickets:
				ticket_channel = bot.get_channel(int(ticket['channel_id']))

				buyer = None
				for member in all_members:
					if member.id == int(ticket['buyer_discord_id']):
						buyer = member
						break

				try:
					ticket_message = await ticket_channel.fetch_message(int(ticket['message_id']))
				except:
					ticket_message = None

				if ticket_channel and buyer and ticket_message:
					await ticket_channel.set_permissions(buyer, read_messages=False, send_messages=False)
					await ticket_channel.edit(category=archive_category)
					await ticket_message.edit(view=None)

					await buyer.send(embed=await discord_utils.build_embed(
						title="Ticket Closed",
						content=f"The ticket you opened for the account #{account['id']} for ${account['price']} has been closed because the sell offer has been taken down by the seller or a staff member.",
						color_type="blue"
					))

			database = bot.get_cog("Database")
			await database.missing_account(account['id'])
			continue

		if status_code != 200:
			print(f"Error while refreshing account {account['id']}")
			return status_code

		print(f"Account #{account['id']}, {account['ign']} going for {account['price']} refreshed successfully!")

	for ticket in tickets:
		status_code = await refresh_ticket(bot, ticket)

		if status_code == 404:
			print(f"Ticket for account #{ticket['account_id']} for discord user with ID {ticket['buyer_discord_id']} MIA, deleting it...")

			database = bot.get_cog("Database")
			await database.delete_ticket(ticket['account_id'], ticket['buyer_discord_id'])
			continue

		if status_code == 208:
			continue

		if status_code != 200:
			print(f"Error while refreshing ticket for account #{ticket['account_id']} for discord user with ID {ticket['buyer_discord_id']}")
			return status_code

		print(f"Ticket for account #{ticket['account_id']} for discord user with ID {ticket['buyer_discord_id']} refreshed successfully!")

	print("Refreshed all accounts and tickets successfully!")

	return 200


async def refresh_account(bot: Bot, account):
	"""
	refreshes the message for a single account
	"""
	try:
		channel = bot.get_channel(int(account['channel_id']))
		message = await channel.fetch_message(int(account['message_id']))
	except Exception as e:
		print(e)
		return 404

	try:
		await message.edit(view=await account_view(bot, str(account['price']).split(".")[0], account['id']))
	except Exception as e:
		print(e)
		return 500

	return 200


async def refresh_ticket(bot: Bot, ticket):
	"""
	refreshes the top message on a ticket (it has buttons)
	"""
	try:
		channel = bot.get_channel(int(ticket['channel_id']))
		message = await channel.fetch_message(int(ticket['message_id']))
	except Exception as e:
		print(e)
		return 404

	try:
		view = discord.ui.View.from_message(message)
		# if the message does not have a view (view=None), skip it as the ticket is in a halted state.
		if discord.ui.View.from_message(message) is None or view.children == [] or view.children == 0:
			print(f"Ticket for account #{ticket['account_id']} for discord user with ID {ticket['buyer_discord_id']} is in a halted state, skipping...")
			return 208

		await message.edit(view=await ticket_view(bot, ticket['account_id'], ticket['buyer_discord_id']))
	except Exception as e:
		print(e)
		return 500

	return 200

async def refresh_admin_message(bot: Bot, config):
	"""
	refreshes the admin message (the one with the buttons to create a new sale)
	"""

	print("Refreshing admin message...")

	if not config['ping_role_id']:
		config['ping_role_id'] = 1

	try:
		channel = bot.get_channel(int(config['admin_channel_id']))
		message = await channel.fetch_message(int(config['admin_message_id']))
	except Exception as e:
		print(e)
		return 404

	try:
		await message.edit(view=admin_view(bot, int(config['main_category_id']), int(config['tickets_category_id']), int(config['ping_role_id']), bool(config['use_ping_role'])))
	except Exception as e:
		print(e)
		return 500


	print("Admin message refreshed successfully!")
	return 200
