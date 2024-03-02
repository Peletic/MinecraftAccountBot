from discord.ext import commands



class Ping(commands.Cog):
	@commands.slash_command(name="ping", description="Pong!")
	async def ping(self, interaction):
		await interaction.response.send_message("Pong!")