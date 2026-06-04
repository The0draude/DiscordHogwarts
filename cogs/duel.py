import json
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

DATA_PATH = "data/players.json"


def load_players():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="duelar", description="Inicia um duelo simples contra outro membro")
    async def duelar(self, interaction: discord.Interaction, adversario: discord.Member):
        if adversario == interaction.user:
            await interaction.response.send_message("Você não pode duelar consigo mesmo.", ephemeral=True)
            return

        data = load_players()
        jogador = str(interaction.user.id)
        oponente = str(adversario.id)

        if jogador not in data or oponente not in data:
            await interaction.response.send_message("Ambos precisam ter ficha criada para duelar.", ephemeral=True)
            return

        ficha_j = data[jogador]
        ficha_o = data[oponente]

        dano_j = random.randint(5, 15) + int(ficha_j.get("poder", 0) // 10)
        dano_o = random.randint(5, 15) + int(ficha_o.get("poder", 0) // 10)

        resultado = (
            f"⚔️ Duelo iniciado entre {interaction.user.mention} e {adversario.mention}\n"
            f"{interaction.user.display_name} causou {dano_j} de dano.\n"
            f"{adversario.display_name} causou {dano_o} de dano."
        )

        await interaction.response.send_message(resultado, ephemeral=False)


async def setup(bot):
    await bot.add_cog(Duel(bot))