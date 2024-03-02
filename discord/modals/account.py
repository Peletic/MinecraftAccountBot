import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils
# from utils import misc, minecraft
from views.ticket import ticket_view


def account_modal(bot:discord.Bot, account_id, config, str_price):
	class AccountModal(Modal):
		def __init__(self):
			super().__init__(title="Please confirm before opening a ticket.", timeout=None)
			self.add_item(InputText(label="Type \"Confirm\" below to proceed.", style=discord.InputTextStyle.short, required=True, placeholder="Confirm", min_length=7, max_length=7))

		async def callback(self, interaction: Interaction):
			try:
				if self.children[0].value.lower() != "confirm":
					return await interaction.response.send_message(embed=await discord_utils.build_embed(
						title="Error",
						content="Your text did not match the required text, please try again. If you believe this was a mistake, please contact a staff member.",
						color_type="red"
					), ephemeral=True)
			except:
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content="Your text did not match the required text, please try again. If you believe this was a mistake, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			# todo maybe move opening ticket message to here, makes it a bit faster and then edit the message with errors if there are any during checks and stuff

			database = bot.get_cog("Database")

			account, status_account = await database.get_account(account_id)
			tickets, status_ticket = await database.get_tickets_for_account(account_id)

			if status_account != 200 or status_ticket != 200:
				return await interaction.response.send_message(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while fetching the account data, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

			for ticket in tickets:
				if int(ticket['buyer_discord_id']) == interaction.user.id:
					return await interaction.response.send_message(embed=await discord_utils.build_embed(
						title="Error",
						content="You already have a ticket open for this account, please close that ticket before opening a new one.",
						color_type="red"
					), ephemeral=True)

			#* checks passed, open ticket

			await interaction.response.defer()
			message = await interaction.followup.send(embed=await discord_utils.build_embed(
				title="Opening Ticket...",
				content=f"Please wait while we open and configure your ticket.",
				color_type="blue"
			), ephemeral=True)

			# get ticket category
			try:
				tickets_category = bot.get_channel(int(config['tickets_category_id']))

				buyer = interaction.user
				seller = bot.get_user(int(account['seller_discord_id']))
				channel = await tickets_category.create_text_channel(name=f"acc{account_id}-{str_price}-{buyer.name}", topic=f"Ticket for account {account_id} with sell price of {str_price} | Buyer: {buyer.name} | Seller: {seller.name}")
			except:
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while creating the ticket channel, please contact a staff member.",
					color_type="red"
				))

			# set the channel permissions
			try:
				await channel.set_permissions(buyer, read_messages=True, send_messages=True)
				await channel.set_permissions(seller, read_messages=True, send_messages=True)
				await channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)
			except:
				await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while setting the channel permissions, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

				return await channel.delete()


			# copy the embed from account['message_id'] to the top of the ticket channel
			sale_message = await bot.get_channel(int(account['channel_id'])).fetch_message(int(account['message_id']))
			sale_embed = sale_message.embeds[0]

			ticket_message = await channel.send(embed=sale_embed, content=f"{seller.mention}, {buyer.mention} is interested in buying account #{account_id} for ${str_price}.", view=await ticket_view(bot, account_id, buyer.id))

			# todo insert ticket upload to database logic
			status_ticket_make = await database.make_ticket_channel(str(channel.id), str(ticket_message.id), account_id, str(interaction.user.id))

			if status_ticket_make != 200:
				await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="There was an error while creating the ticket, please contact a staff member.",
					color_type="red"
				), ephemeral=True)

				return await channel.delete()


			return await message.edit(embed=await discord_utils.build_embed(
				title="Success",
				content=f"Your ticket has been created and is now open. You can find it in <#{channel.id}>.",
				color_type="green"
			))



	return AccountModal()