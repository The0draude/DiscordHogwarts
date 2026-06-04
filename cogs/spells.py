import json
import os

import discord
from discord import app_commands
from discord.ext import commands

DATA_PATH = "data/players.json"


def load_players():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Spells(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lista-feiticos", description="Mostra os feitiços disponíveis no sistema")
    async def lista_feiticos(self, interaction: discord.Interaction):
        feiticos = [
            "expelliarmus", "stupefy", "protego", "flipendo",
            "reducto", "sectumsempra", "crucio", "avada_kedavra"
        ]
        await interaction.response.send_message(
            "Feitiços disponíveis: " + ", ".join(feiticos),
            ephemeral=True,
        )

    @app_commands.command(name="meu-feitiço", description="Exibe os feitiços liberados da sua ficha")
    async def meu_feitico(self, interaction: discord.Interaction):
        data = load_players()
        uid = str(interaction.user.id)

        if uid not in data:
            await interaction.response.send_message("Você ainda não tem ficha. Peça a um ADM para criar uma.", ephemeral=True)
            return

        ficha = data[uid]
        desbloqueados = [nome for nome, info in ficha.get("feiticos", {}).items() if info.get("desbloqueado")]
        bloqueados = [nome for nome, info in ficha.get("feiticos", {}).items() if not info.get("desbloqueado")]

        msg = [
            f"📋 Sua ficha: **{ficha.get('nome', interaction.user.display_name)}**",
            f"❤️ HP: {ficha.get('hp_max', 0)}",
            f"⚡ Poder: {ficha.get('poder', 0)}",
            f"🛡️ Resistência: {ficha.get('resistencia', 0)}%",
            f"💥 Max Hits (Duelo): {ficha.get('max_hits', 3)}",
            "",
            "✅ Feitiços desbloqueados: " + (", ".join(desbloqueados) if desbloqueados else "nenhum"),
            "🔒 Feitiços bloqueados: " + (", ".join(bloqueados) if bloqueados else "nenhum"),
        ]
        await interaction.response.send_message("\n".join(msg), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Spells(bot))