import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")
    
    @commands.command()
    async def info(self, ctx):
        await ctx.send("Commands: !help, !roll")

    @app_commands.command(name="info", description="Provide Information about the bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="CS 407 Bot",
            url="https://github.com/anvovn/cs407-project",
           description="Github link",
           color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8dm1kH_dIjn2dtMwkgO2wbdHunzc2ayEUZQ&s")
        embed.add_field(name="Commands", value="List of Commands", inline=False)
        embed.set_footer(text="Creator: An, Tyler")
        embed.set_author(
            name=interaction.user.name,
            url="https://chatgpt.com/?ref=glasp",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else ""
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))