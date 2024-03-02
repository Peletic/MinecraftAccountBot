import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils
from utils import misc, minecraft

from views.account import account_view

def admin_modal(bot: discord.Bot, main_category_id, tickets_category_id, ping_role_id, use_ping_role):
	class AdminModal(Modal):
		def __init__(self):
			super().__init__(title="Put an account up for sale", timeout=None)
			self.add_item(InputText(label="Account IGN", placeholder="Minecraft account's name"))
			self.add_item(InputText(label="Price", placeholder="Price in USD"))
			self.add_item(InputText(label="Payment methods", placeholder="PayPal, BTC, etc."))
			self.add_item(InputText(label="Extra info", placeholder="Extra info about the account", required=False))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			message = await interaction.followup.send(embed=await discord_utils.build_embed(
				title="Creating sell offer...",
				content="Checking information and gathering data from APIs, please wait...",
				color_type="purple"
			), ephemeral=True)

			# get the values from the inputs
			ign = self.children[0].value
			price = misc.obtain_float(self.children[1].value)
			payment_methods = self.children[2].value
			extra_info = self.children[3].value if self.children[3] else "Not provided"
			seller_discord_id = interaction.user.id

			if extra_info == "": extra_info = "Not provided"

			if not price:
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content="Invalid price, please make sure it's a valid float (IE: 727.69 or 420,69))",
					color_type="red"
				))

			try:
				info = await minecraft.extract_info(ign)
			except Exception as e:
				# todo pretty embed
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content=f"Error while extracting info from the account: {e}",
					color_type="red"
				))

			# obtain the Database cog
			database = bot.get_cog("Database")

			# create the account in the database
			account_id, status_code = await database.start_sell_offer(ign, info['uuid'], price, payment_methods, extra_info, "FOR_SALE", seller_discord_id)

			if status_code != 200 or not account_id:
				#todo handle the error and pretty embeds
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content=f"Error while creating the account in the database: {status_code}",
					color_type="red"
				))

			try:
				embed, sblevel = await discord_utils.make_sale_embed(info, price, payment_methods, extra_info, seller_discord_id)
			except Exception as e:
				# todo pretty embed
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content=f"Error while creating the embed: {e}",
					color_type="red"
				))

			# create a new channel in the main category
			main_category = bot.get_channel(main_category_id)

			# create the channel
			# transforms the price float into a string, removes the decimal part
			str_price = str(price).split(".")[0]
			str_sblevel = str(sblevel).split(".")[0]

			channel = await main_category.create_text_channel(name=f"💲{str_price}｜⭐{str_sblevel}｜🔰{account_id}")

			await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
			await channel.set_permissions(interaction.guild.default_role, read_messages=True, send_messages=False)


			message_content = f"<@&{ping_role_id}>" if use_ping_role else None
			sale_message = await channel.send(content=message_content, embed=embed, view=await account_view(bot, str_price, account_id))

			# complete the sell offer in the database
			status_code = await database.complete_sell_offer(account_id, channel.id, sale_message.id)

			if status_code != 200:
				# todo handle the error (this includes removing the channel and message, as well as the incomplete sell offer in the database)
				return await message.edit(embed=await discord_utils.build_embed(
					title="Error",
					content=f"Error while completing the sell offer in the database: {status_code}",
					color_type="red"
				))


			return await message.edit(embed=await discord_utils.build_embed(
				title="Sell offer created!",
				content=f"The sell offer has been created successfully in channel <#{channel.id}>!",
				color_type="green"
			), view=None)



	return AdminModal()