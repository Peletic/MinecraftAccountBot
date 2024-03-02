import discord
import datetime
import aiohttp
import json

from utils import misc

with open('./config.json') as f:
	config = json.load(f)

BOT_TOKEN = config['DISCORD_BOT_TOKEN'] if 'DISCORD_BOT_TOKEN' in config else None
if BOT_TOKEN is None or BOT_TOKEN == "": raise Exception('DISCORD_BOT_TOKEN is not defined in config.json')

avatar_hash = None
colors = {
    "red": 0xE81F55,
    "green": 0xA9EA74,
    "purple": 0xFF4CAE,
    "blue": 0x27CDEA
}


async def get_hash(user_id=269625969705353218):
	"""
	Gets the avatar hash from the discord API
	"""
	url = f"https://discord.com/api/users/{user_id}"
	headers = {'accept': 'application/json', 'Authorization': f"Bot {BOT_TOKEN}"}

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers) as response:
			if response.status == 200:
				data = await response.json()
				return data['avatar']
			else: return None


async def get_avatar_url(user_id=269625969705353218):
	"""
	Gets the avatar url from the discord API
	"""

	if user_id == 269625969705353218:
		global avatar_hash

		if avatar_hash is None:
			avatar_hash = await get_hash()

		return f'https://cdn.discordapp.com/avatars/269625969705353218/{avatar_hash}.webp?size=512'
	else:
		hash = await get_hash(user_id)

		return f'https://cdn.discordapp.com/avatars/{user_id}/{hash}.webp?size=512'


async def build_embed(title, content, color_type, use_footer=True, use_thumbnail=False, use_timestamp=True):
	"""
	Builds an embed with the given parameters (made for consistency between embeds and ease of use while building them)
	"""
	if color_type not in colors.keys(): raise Exception("Invalid color type!")

	# avatar_url = await get_avatar_url()

	if use_timestamp:
		embed = discord.Embed(
			title=title,
			description=content,
			color=colors[color_type],
			timestamp=datetime.datetime.now()
		)
	else:
		embed = discord.Embed(
			title=title,
			description=content,
			color=colors[color_type]
		)

	if use_footer:
		embed.set_footer(text=f"Flux Bot")

	if use_thumbnail:
		embed.set_thumbnail(url="https://i.imgur.com/HSgldiA.png")

	return embed


async def is_admin(interaction):
	"""
	Checks if the user in the interaction is an admin in that guild
	"""
	if interaction.user.guild_permissions.administrator:
		return True
	else:
		return False


async def fetch_webhook(url):
	"""
	Returns a webhook object and a session object
	"""
	try:
		session = aiohttp.ClientSession()

		webhook = discord.Webhook.from_url(url, session=session)

		return webhook, session
	except Exception as e:
		return None, None


async def make_sale_embed(info, price, payment_methods, extra_info, seller_discord_id):
	embed = await build_embed(title="Account Information", content=f"Rank: \n**{info['rank']}**", color_type="blue", use_footer=False, use_thumbnail=False, use_timestamp=False)
	embed.add_field(name="Skyblock Level", value=f"**{info['sblevel']}**")
	embed.add_field(name="Skill Average", value=f"**{info['skillavg']}**")

	slayer_string = ""
	# transform all the levels into a "level / level / level" string
	for _, level in info['slayers'].items():
		slayer_string += f"{level} / "
	# remove the last " / "
	slayer_string = slayer_string[:-3]


	embed.add_field(name="Slayer", value=f"**{slayer_string}**")
	embed.add_field(name="Weight", value=f"Senither: **{misc.add_dots(int(info['senither_weight']))}**\nLily: **{misc.add_dots(int(info['lily_weight']))}**")
	embed.add_field(name="Dungeons", value=f"Catacombs: **{info['catacombs_level']}**\nAvg Class Lvl: **{info['catacombs_class_level_average']}**")
	embed.add_field(name="Minions", value=f"Total Slots: **{info['minion_slots']}**\nBonus Slots: **{info['bonus_minion_slots']}**")
	embed.add_field(name="Mining", value=f"HOTM Level: **{info['hotm_level']}**\nMithril Powder: **{info['mithril_powder']}**\nGemstone Powder: **{info['gemstone_powder']}**")
	embed.add_field(name="Networth", value=f"Total: **{info['total_nw']}**\nUnsoulbound: **{info['unsoulbound_nw']}**\nLiquid: **{info['liquid']}**")
	embed.add_field(name="Price & Details", value=f"Price: **${price}**\nSeller: <@{seller_discord_id}>\nPayment Methods: **{payment_methods}**\nExtra Info: **{extra_info}**")
	embed.set_thumbnail(url="https://crafatar.com/renders/body/640a5372780b4c2ab7e78359d2f9a6a8?overlay")
	embed.set_footer(text=f"Made by @r3dlust | Last updated")
	embed.timestamp = datetime.datetime.now()

	return embed, info['sblevel']