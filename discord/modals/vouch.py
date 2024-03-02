import discord

from discord.interactions import Interaction
from discord.ui import Modal, InputText

from utils import discord as discord_utils


async def vouch_modal(bot:discord.Bot, message, vouchee_id, vouch_anonymously: bool):
	database = bot.get_cog("Database")
	config, _ = await database.get_config()
	vouch_channel = bot.get_channel(int(config['vouch_channel_id']))


	class VouchModal(Modal):
		def __init__(self):
			super().__init__(title="Vouch Confirmation", timeout=None)
			self.add_item(InputText(label="Please leave a small comment for the seller", style=discord.InputTextStyle.long, required=False, placeholder="Comment"))

		async def callback(self, interaction: Interaction):
			await interaction.response.defer()

			comment = self.children[0].value

			vouchee = bot.get_user(vouchee_id)

			content = f"**Vouch for {vouchee.name}**\n\n**Note:** {comment}" if comment else f"**Vouch for account sale**"

			embed = await discord_utils.build_embed(
				title="",
				content=content,
				color_type="blue"
			)

			if vouch_anonymously:
				embed.set_author(name="Anonymous", icon_url="https://i.imgur.com/twuK5J0.jpeg")
				embed.set_footer(text="This vouch was left anonymously")
			else:
				embed.set_author(name=f"{interaction.user.name}", icon_url=await discord_utils.get_avatar_url(interaction.user.id))
				embed.set_footer(text=f"This vouch was left by user {interaction.user.id}")


			await vouch_channel.send(embed=embed)

			await message.edit(embed=await discord_utils.build_embed(
				title="Vouch successful",
				content=f"Thank you for vouching! Have a nice day!",
				color_type="green"
			), view=None)


	return VouchModal()