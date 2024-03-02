import os
import aiosqlite as sqlite3
from discord.ext import commands

class Database(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# if the database file doesnt exist, dont create it yet
		if not os.path.exists('./database/database.db'):
			self.database = None
		else:
			self.database = './database/database.db'


	async def create_database(self):
		# create the database file
		try:
			async with sqlite3.connect('./database/database.db') as database:
				await database.execute('''
					CREATE TABLE IF NOT EXISTS [accounts] (
						[id] INTEGER PRIMARY KEY,
						[ign] TEXT,
						[channel_id] TEXT,
						[message_id] TEXT,
						[uuid] TEXT,
						[price] FLOAT,
						[payment_methods] TEXT,
						[extra_info] TEXT,
						[status] TEXT,
						[seller_discord_id] TEXT,
						[buyer_discord_id] TEXT
 					)
				''')

				await database.execute('''
					CREATE TABLE IF NOT EXISTS [config] (
						[main_category_id] TEXT,
						[admin_channel_id] TEXT,
						[admin_message_id] TEXT,
						[ping_role_id] TEXT,
						[use_ping_role] BOOLEAN,
						[tickets_category_id] TEXT,
						[seller_role_id] TEXT,
						[vouch_channel_id] TEXT,
						[archive_category_id] TEXT
					)
				''')

				await database.execute('''
					CREATE TABLE [tickets] (
						[channel_id] TEXT,
						[message_id] TEXT,
						[account_id] INTEGER,
						[buyer_discord_id] TEXT,
						FOREIGN KEY ([account_id]) REFERENCES [accounts] ([id])
					)
				''')

				await database.commit()

				self.database = './database/database.db'

				return 200
		except Exception as e:
			print(e)
			return 500


	async def setup_database(self, main_category_id:str, admin_channel_id:str, admin_message_id:str, ping_role_id:str, use_ping_role:bool, tickets_category_id:str, seller_role_id:str, vouch_channel_id:str, archive_category_id:str):
		# setup the database with the config
		if not self.database:
			return 503

		# checks if there already is an entry in the config table (there can only be one)
		async with sqlite3.connect(self.database) as database:
			async with database.execute('''SELECT * FROM [config]''') as cursor:
				if await cursor.fetchone():
					return 409
				else:
					await database.execute('''INSERT INTO [config] (main_category_id, admin_channel_id, admin_message_id, ping_role_id, use_ping_role, tickets_category_id, seller_role_id, vouch_channel_id, archive_category_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (main_category_id, admin_channel_id, admin_message_id, ping_role_id, use_ping_role, tickets_category_id, seller_role_id, vouch_channel_id, archive_category_id))

					await database.commit()

					return 200



	async def start_sell_offer(self, ign:str, uuid:str, price:float, payment_methods:str, extra_info:str, status:str, seller_discord_id:str):
		# stats a sell offer before the message and channel are created
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''INSERT INTO [accounts] (ign, uuid, price, payment_methods, extra_info, status, seller_discord_id) VALUES (?, ?, ?, ?, ?, ?, ?)''', (ign, uuid, price, payment_methods, extra_info, status, seller_discord_id))

				async with database.execute('''SELECT last_insert_rowid()''') as cursor:
					id = (await cursor.fetchone())[0]

				await database.commit()
				return (id, 200)

		except Exception as e:
			print(e)
			return (None, 500)


	async def complete_sell_offer(self, id:int, channel_id:str, message_id:str):
		# completes a sell offer after the message and channel are created
		if not self.database:
			return 503

		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''UPDATE [accounts] SET channel_id = ?, message_id = ? WHERE id = ?''', (channel_id, message_id, id))
				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500


	async def create_ticket(self, channel_id:str, message_id:str, account_id:int, buyer_discord_id:str):
		# create the ticket in the database
		if not self.database:
			return 503

		# checks if that user already has a ticket for that account
		try:
			async with self.database as database:
				async with database.execute('''
					SELECT * FROM [tickets] WHERE [account_id] = ? AND [buyer_discord_id] = ?
				''', (account_id, buyer_discord_id)) as cursor:
					if await cursor.fetchone():
						return 409
					else:
						await database.execute('''
							INSERT INTO [tickets] (channel_id, message_id, account_id, buyer_discord_id)
							VALUES (?, ?, ?, ?)
						''', (channel_id, message_id, account_id, buyer_discord_id))

						await database.commit()

						return 200
		except Exception as e:
			print(e)
			return 500


	async def get_config(self):
		# get the config from the database
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				# Set the row factory to return rows as dictionaries
				database.row_factory = sqlite3.Row

				async with database.cursor() as cursor:
					await cursor.execute('''SELECT * FROM [config]''')
					config = await cursor.fetchone()
					if config:
						# Convert the sqlite3.Row object to a dict
						config = dict(config)
						config['use_ping_role'] = bool(config['use_ping_role'])

					return (config, 200)
		except Exception as e:
			print(e)
			return (None, 500)


	async def get_accounts(self):
		# get all the accounts from the database
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				# Set the row factory to return rows as dictionaries
				database.row_factory = sqlite3.Row

				async with database.cursor() as cursor:
					await cursor.execute('''SELECT * FROM [accounts]''')
					accounts = await cursor.fetchall()
					if accounts:
						# Convert the sqlite3.Row object to a dict
						accounts = [dict(account) for account in accounts]

					return (accounts, 200)
		except Exception as e:
			print(e)
			return (None, 500)


	async def get_tickets(self):
		# get all the tickets from the database
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				# Set the row factory to return rows as dictionaries
				database.row_factory = sqlite3.Row

				async with database.cursor() as cursor:
					await cursor.execute('''SELECT * FROM [tickets]''')
					tickets = await cursor.fetchall()
					if tickets:
						# Convert the sqlite3.Row object to a dict
						tickets = [dict(ticket) for ticket in tickets]

					return (tickets, 200)
		except Exception as e:
			print(e)
			return (None, 500)


	async def get_account(self, account_id: int):
		# get a single account from the database
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				# Set the row factory to return rows as dictionaries
				database.row_factory = sqlite3.Row

				async with database.cursor() as cursor:
					await cursor.execute('''SELECT * FROM [accounts] WHERE [id] = ?''', (account_id,))
					account = await cursor.fetchone()
					if account:
						# Convert the sqlite3.Row object to a dict
						account = dict(account)

					return (account, 200)
		except Exception as e:
			print(e)
			return (None, 500)


	async def get_tickets_for_account(self, account_id: int):
		# get all the tickets for a single account from the database
		if not self.database:
			return (None, 503)

		try:
			async with sqlite3.connect(self.database) as database:
				# Set the row factory to return rows as dictionaries
				database.row_factory = sqlite3.Row

				async with database.cursor() as cursor:
					await cursor.execute('''SELECT * FROM [tickets] WHERE [account_id] = ?''', (account_id,))
					tickets = await cursor.fetchall()
					if tickets:
						# Convert the sqlite3.Row object to a dict
						tickets = [dict(ticket) for ticket in tickets]

					return (tickets, 200)
		except Exception as e:
			print(e)
			return (None, 500)


	async def make_ticket_channel(self, channel_id:str, message_id:str, account_id:int, buyer_discord_id:str):
		# make a ticket channel in the database
		if not self.database:
			return 503

		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''INSERT INTO [tickets] (channel_id, message_id, account_id, buyer_discord_id) VALUES (?, ?, ?, ?)''', (channel_id, message_id, account_id, buyer_discord_id))

				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500


	async def delete_account(self, account_id):
		# delete an account from the database
		if not self.database:
			return 503

		# delete all tickets for that account
		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''DELETE FROM [tickets] WHERE [account_id] = ?''', (account_id,))

				await database.commit()
		except Exception as e:
			print(e)
			return 500


		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''DELETE FROM [accounts] WHERE [id] = ?''', (account_id,))

				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500


	async def delete_ticket(self, account_id:int, buyer_discord_id:str):
		# delete a ticket from the database
		if not self.database:
			return 503

		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''DELETE FROM [tickets] WHERE [account_id] = ? AND [buyer_discord_id] = ?''', (account_id, buyer_discord_id))

				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500


	async def sell_account(self, account_id):
		# delete all tickets for that account
		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''DELETE FROM [tickets] WHERE [account_id] = ?''', (account_id,))

				await database.commit()
		except Exception as e:
			print(e)
			return 500

		# change status from FOR_SALE to SOLD
		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''UPDATE [accounts] SET status = ? WHERE id = ?''', ("SOLD", account_id))

				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500


	async def missing_account(self, account_id:int):
		# delete all tickets for that account
		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''DELETE FROM [tickets] WHERE [account_id] = ?''', (account_id,))

				await database.commit()
		except Exception as e:
			print(e)
			return 500

		try:
			async with sqlite3.connect(self.database) as database:
				await database.execute('''UPDATE [accounts] SET status = ? WHERE id = ?''', ("MISSING", account_id))

				await database.commit()
				return 200
		except Exception as e:
			print(e)
			return 500