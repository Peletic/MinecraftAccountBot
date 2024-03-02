import aiohttp
import asyncio
import json

from utils.misc import representTBMK

with open('./config.json') as f:
	config = json.load(f)

# API_KEY = "ac13a5f7-d660-4356-95ae-6e8f1a34bb7a"
API_KEY = config['HYPIXEL_API_KEY'] if 'HYPIXEL_API_KEY' in config else None

if API_KEY is None or API_KEY == "": raise Exception('HYPIXEL_API_KEY is not defined in config.json')

TIMEOUT = 30


async def get_username_info(username):
	"""
	Uses the Mojang API to get the UUID of a player.
	"""
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as response:
				if response.status == 200:
					return await response.json()
				else:
					return None
	except: return None


async def get_hypixel_info(session, uuid):
	try:
		async with session.get(f"https://api.hypixel.net/player?key={API_KEY}&uuid={uuid}", timeout=TIMEOUT) as response:
			if response.status == 200:
				return await response.json()
			else:
				print(f"Error fetching Hypixel info: {response.status}")
				print(f"Response: {await response.text()}")
				return None
	except aiohttp.ClientError as e:
		# Log or print the specific error
		print(f"Error fetching Hypixel info: {e}")
		return None


async def get_shiiyu_info(session, username):
	try:
		# little bit hacky fix bc of shiiyu's api needing the profiles to be cached b4hand
		await session.get(f"http://localhost/profiles/{username}")
		async with session.get(f"http://localhost/api/v2/profile/{username}") as response:
			if response.status == 200:
				print(f"Response: {await response.json()}")
				return await response.json()
			else:
				print(f"Response: {await response.json()}")
				return None
	except aiohttp.ClientError as e:
		# Log or print the specific error
		print(f"Error fetching Shiiyu info: {e}")
		return None


async def resolve_biggest_profile(shiiyu_info: dict):
	"""
	Returns the profile ID of the profile with the highest net-worth, given a user's shiiyu_info
	"""
	biggest_profile_id = 0
	biggest_profile_networth = 0

	for profile_id in shiiyu_info["profiles"]:
		if shiiyu_info["profiles"][profile_id]["data"]["networth"]["networth"] > biggest_profile_networth:
			biggest_profile_networth = shiiyu_info["profiles"][profile_id]["data"]["networth"]["networth"]
			biggest_profile_id = shiiyu_info["profiles"][profile_id]["profile_id"]

	return biggest_profile_id


async def resolve_rank(hypixel_info: dict):
	"""
	Returns the rank of a player, given their hypixel_info
	"""
	if 'monthlyPackageRank' in hypixel_info['player'] and not hypixel_info['player']['monthlyPackageRank'] == 'NONE':
		rank = 'MVP++'
	elif 'newPackageRank' in hypixel_info['player']:
		rank = hypixel_info['player']['newPackageRank']
		if rank == "MVP_PLUS": rank = "MVP+"
		elif rank == "MVP_PLUS_PLUS": rank = "MVP++"
		elif rank == "NONE": rank = "Default"
		elif rank == "VIP_PLUS": rank = "VIP+"
		elif rank == "VIP": rank = "VIP"
	elif 'packageRank' in hypixel_info['player']:
		rank = hypixel_info['player']['packageRank']
		if rank == "MVP_PLUS": rank = "MVP+"
		elif rank == "MVP_PLUS_PLUS": rank = "MVP++"
		elif rank == "NONE": rank = "Default"
		elif rank == "VIP_PLUS": rank = "VIP+"
		elif rank == "VIP": rank = "VIP"
	else:
		rank = "Default"

	return rank


async def extract_info(username):
	"""
	Extracts all needed information for creating sell offers from the username provided.
	"""

	#*######################*#
	#* Fetching Information *#
	#*######################*#


	user_info = await get_username_info(username)

	if not user_info:
		raise Exception("Invalid username")
	else:
		uuid = user_info['id']

		#! This properly capitalizes the username (e.g. "notch" -> "Notch")
		username = user_info['name']


		async with aiohttp.ClientSession() as session:
			hypixel_info, shiiyu_info = await asyncio.gather(
				get_hypixel_info(session, uuid),
				get_shiiyu_info(session, username)
			)
		print(f"{shiiyu_info}")

		if not hypixel_info or not shiiyu_info:
			raise Exception(f"Failed to get {'Hypixel' if not hypixel_info else 'SkyCrypt'} stats for {username}")




	#*#######################*#
	#* Selecting Information *#
	#*#######################*#

	if len(shiiyu_info["profiles"]) == 0:
		raise Exception(f"{username} has no SkyBlock profiles")

	biggest_profile_id = await resolve_biggest_profile(shiiyu_info)

	#! Rank
	try:
		rank = await resolve_rank(hypixel_info)
	except: rank = "N/A"

	#! Skill Average
	try:
		skillavg = round(shiiyu_info["profiles"][biggest_profile_id]["data"]["average_level_no_progress"], 1)
	except: skillavg = "N/A"

	#! Catacombs Level
	try:
		catacombs_level = shiiyu_info["profiles"][biggest_profile_id]["data"]["dungeons"]["catacombs"]["level"]["level"]
	except: catacombs_level = "N/A"

	#! Catacombs Class Level Average
	try:
		levels = []
		for class_ in shiiyu_info["profiles"][biggest_profile_id]["data"]["dungeons"]['classes']:
			levels.append(float(shiiyu_info["profiles"][biggest_profile_id]["data"]["dungeons"]['classes'][class_]['experience']['unlockableLevelWithProgress']))

		catacombs_class_level_average = round(sum(levels) / len(levels), 1)
	except: catacombs_class_level_average = "N/A"


	#! Senither Weight
	try:
		senither_weight = round(shiiyu_info["profiles"][biggest_profile_id]["data"]["weight"]["senither"]["overall"], 0)
		senither_weight = str(int(senither_weight))
	except: senither_weight = "N/A"

	#! Lily Weight
	try:
		lily_weight = round(shiiyu_info["profiles"][biggest_profile_id]["data"]["weight"]["lily"]["total"], 0)
		lily_weight = str(int(lily_weight))
	except: lily_weight = "N/A"

	#! Skyblock Level
	try:
		sblevelProgress = str(shiiyu_info["profiles"][biggest_profile_id]["data"]["skyblock_level"]["progress"])
		sblevelProgress = sblevelProgress.split(".")
		# only gets the first character of the progress, so 1.2 becomes 1.2, 1.23 becomes 1.2, 1.234 becomes 1.2, etc
		for char in sblevelProgress[1]:
			sblevelProgress[1] = char
			break
		sblevel = str(shiiyu_info["profiles"][biggest_profile_id]["data"]["skyblock_level"]["level"]) + "." + sblevelProgress[1]
	except: sblevel = "N/A"

	#! Slayer Levels
	try:
		slayers = {}
		#! Revenant Slayer
		try:
			slayers['zombie'] = int(shiiyu_info["profiles"][biggest_profile_id]["data"]["slayers"]["zombie"]["level"]["currentLevel"])
		except: slayers['zombie'] = 0

		#! Tara Slayer
		try:
			slayers['spider'] = int(shiiyu_info["profiles"][biggest_profile_id]["data"]["slayers"]["spider"]["level"]["currentLevel"])
		except: slayers['spider'] = 0

		#! Sven Slayer
		try:
			slayers['wolf'] = int(shiiyu_info["profiles"][biggest_profile_id]["data"]["slayers"]["wolf"]["level"]["currentLevel"])
		except: slayers['wolf'] = 0

		#! Voidgloom Slayer
		try:
			slayers['enderman'] = int(shiiyu_info["profiles"][biggest_profile_id]["data"]["slayers"]["enderman"]["level"]["currentLevel"])
		except: slayers['enderman'] = 0

		#! Blaze Slayer
		try:
			slayers['blaze'] = int(shiiyu_info["profiles"][biggest_profile_id]["data"]["slayers"]["blaze"]["level"]["currentLevel"])
		except: slayers['blaze'] = 0
	except:
		slayers = {
			"zombie": 0,
			"spider": 0,
			"wolf": 0,
			"enderman": 0,
			"blaze": 0
		}

	#! Networth
	try:
		total_nw = shiiyu_info["profiles"][biggest_profile_id]["data"]["networth"]["networth"]
		unsoulbound_nw = shiiyu_info["profiles"][biggest_profile_id]["data"]["networth"]["unsoulboundNetworth"]

		soulbound_nw = total_nw - unsoulbound_nw
		soulbound_nw = representTBMK(soulbound_nw)

		total_nw = representTBMK(total_nw)

		unsoulbound_nw = representTBMK(unsoulbound_nw)

		liquid = shiiyu_info["profiles"][biggest_profile_id]["data"]["networth"]["purse"] + shiiyu_info["profiles"][biggest_profile_id]["data"]["networth"]["bank"]
		liquid = representTBMK(liquid)
	except:
		total_nw = "N/A"
		unsoulbound_nw = "N/A"
		soulbound_nw = "N/A"
		liquid = "N/A"

	#! HOTM Level
	try:
		hotm_level = shiiyu_info["profiles"][biggest_profile_id]["data"]["mining"]["core"]["tier"]["level"]
	except: hotm_level = "N/A"

	#! Mithril Powder
	try:
		mithril_powder = shiiyu_info["profiles"][biggest_profile_id]["data"]["mining"]["core"]["powder"]["mithril"]["total"]
		mithril_powder = representTBMK(mithril_powder)
	except: mithril_powder = "N/A"

	#! Gemstone Powder
	try:
		gemstone_powder = shiiyu_info["profiles"][biggest_profile_id]["data"]["mining"]["core"]["powder"]["gemstone"]["total"]
		gemstone_powder = representTBMK(gemstone_powder)
	except: gemstone_powder = "N/A"

	#! Minion Slots (Total)
	try:
		minion_slots = shiiyu_info["profiles"][biggest_profile_id]["data"]["minion_slots"]["currentSlots"]
	except: minion_slots = "N/A"

	#! Bonus Minion Slots
	try:
		bonus_minion_slots = f'{shiiyu_info["profiles"][biggest_profile_id]["data"]["misc"]["profile_upgrades"]["minion_slots"]}/5'
	except: bonus_minion_slots = "N/A"


	return {
		"username": username,
		"uuid": uuid,
		"rank": rank,
		"skillavg": skillavg,
		"catacombs_level": catacombs_level,
		"catacombs_class_level_average": catacombs_class_level_average,
		"senither_weight": senither_weight,
		"lily_weight": lily_weight,
		"sblevel": sblevel,
		"slayers": slayers,
		"total_nw": total_nw,
		"unsoulbound_nw": unsoulbound_nw,
		"soulbound_nw": soulbound_nw,
		"liquid": liquid,
		"hotm_level": hotm_level,
		"mithril_powder": mithril_powder,
		"gemstone_powder": gemstone_powder,
		"minion_slots": minion_slots,
		"bonus_minion_slots": bonus_minion_slots
	}

# print(asyncio.run(extract_info("yyz3rowned")))