import discord
from discord.ext import commands
import config

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = ["cogs.spells", "cogs.duel", "cogs.admin"]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online como {bot.user}")

async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())