import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import config

DATA_PATH = "data/players.json"

SPELLS_DEFAULT = {
    "expelliarmus": {"desbloqueado": True,  "cooldown": 2},
    "stupefy":      {"desbloqueado": True,  "cooldown": 2},
    "protego":      {"desbloqueado": True,  "cooldown": 2},
    "flipendo":     {"desbloqueado": True,  "cooldown": 2},
    "reducto":      {"desbloqueado": False, "cooldown": 2},
    "sectumsempra": {"desbloqueado": False, "cooldown": 2},
    "crucio":       {"desbloqueado": False, "cooldown": 2},
    "avada_kedavra":{"desbloqueado": False, "cooldown": 2},
}

def load():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_adm(interaction: discord.Interaction):
    return any(r.name == config.ADM_ROLE_NAME for r in interaction.user.roles)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Criar ficha ──────────────────────────────────────────────────────────
    @app_commands.command(name="criar-ficha", description="Cria a ficha de um personagem")
    async def criar_ficha(self, interaction: discord.Interaction, usuario: discord.Member):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)

        if uid in data:
            await interaction.response.send_message(f"{usuario.display_name} já tem ficha.", ephemeral=True)
            return

        data[uid] = {
            "nome": usuario.display_name,
            "hp_max": 80,
            "poder": 100,
            "resistencia": 0,
            "feiticos": SPELLS_DEFAULT.copy()
        }
        save(data)
        await interaction.response.send_message(f"✅ Ficha de **{usuario.display_name}** criada com sucesso!")

    # ── Ver ficha ─────────────────────────────────────────────────────────────
    @app_commands.command(name="ver-ficha", description="Exibe a ficha de um personagem")
    async def ver_ficha(self, interaction: discord.Interaction, usuario: discord.Member):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)

        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return

        p = data[uid]
        linhas = [
            f"**📋 Ficha de {p['nome']}**",
            f"❤️ HP máximo: `{p['hp_max']}`",
            f"⚡ Poder mágico: `{p['poder']}`",
            f"🛡️ Resistência: `{p['resistencia']}%`",
            "",
            "**Feitiços:**"
        ]
        for nome, info in p["feiticos"].items():
            status = "✅" if info["desbloqueado"] else "🔒"
            linhas.append(f"{status} `{nome}` — cooldown: {info['cooldown']} turnos")

        await interaction.response.send_message("\n".join(linhas), ephemeral=True)

    # ── Set HP ────────────────────────────────────────────────────────────────
    @app_commands.command(name="set-hp", description="Define o HP máximo de um personagem")
    async def set_hp(self, interaction: discord.Interaction, usuario: discord.Member, valor: int):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return

        data[uid]["hp_max"] = valor
        save(data)
        await interaction.response.send_message(f"❤️ HP de **{data[uid]['nome']}** definido para `{valor}`.")

    # ── Set Poder ─────────────────────────────────────────────────────────────
    @app_commands.command(name="set-poder", description="Define o poder mágico de um personagem")
    async def set_poder(self, interaction: discord.Interaction, usuario: discord.Member, valor: int):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return

        data[uid]["poder"] = valor
        save(data)
        await interaction.response.send_message(f"⚡ Poder de **{data[uid]['nome']}** definido para `{valor}`.")

    # ── Set Resistência ───────────────────────────────────────────────────────
    @app_commands.command(name="set-resist", description="Define a resistência (%) de um personagem")
    async def set_resist(self, interaction: discord.Interaction, usuario: discord.Member, valor: int):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return

        data[uid]["resistencia"] = valor
        save(data)
        await interaction.response.send_message(f"🛡️ Resistência de **{data[uid]['nome']}** definida para `{valor}%`.")

    # ── Unlock feitiço ────────────────────────────────────────────────────────
    @app_commands.command(name="unlock-spell", description="Desbloqueia um feitiço para um personagem")
    async def unlock_spell(self, interaction: discord.Interaction, usuario: discord.Member, feitico: str):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        feitico = feitico.lower()

        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return
        if feitico not in data[uid]["feiticos"]:
            await interaction.response.send_message(f"Feitiço `{feitico}` não existe.", ephemeral=True)
            return

        data[uid]["feiticos"][feitico]["desbloqueado"] = True
        save(data)
        await interaction.response.send_message(f"✅ `{feitico}` desbloqueado para **{data[uid]['nome']}**.")

    # ── Lock feitiço ──────────────────────────────────────────────────────────
    @app_commands.command(name="lock-spell", description="Bloqueia um feitiço de um personagem")
    async def lock_spell(self, interaction: discord.Interaction, usuario: discord.Member, feitico: str):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        feitico = feitico.lower()

        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return
        if feitico not in data[uid]["feiticos"]:
            await interaction.response.send_message(f"Feitiço `{feitico}` não existe.", ephemeral=True)
            return

        data[uid]["feiticos"][feitico]["desbloqueado"] = False
        save(data)
        await interaction.response.send_message(f"🔒 `{feitico}` bloqueado para **{data[uid]['nome']}**.")

    # ── Set cooldown ──────────────────────────────────────────────────────────
    @app_commands.command(name="set-cooldown", description="Define o cooldown de um feitiço para um personagem")
    async def set_cooldown(self, interaction: discord.Interaction, usuario: discord.Member, feitico: str, valor: int):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)
        feitico = feitico.lower()

        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return
        if feitico not in data[uid]["feiticos"]:
            await interaction.response.send_message(f"Feitiço `{feitico}` não existe.", ephemeral=True)
            return

        data[uid]["feiticos"][feitico]["cooldown"] = valor
        save(data)
        await interaction.response.send_message(f"⏱️ Cooldown de `{feitico}` para **{data[uid]['nome']}** definido para `{valor}` turnos.")

    # ── Set max hits (acertos máximos) ────────────────────────────────────────
    @app_commands.command(name="set-max-hits", description="Define quantos acertos máximos o usuário aguenta antes de ser derrotado")
    async def set_max_hits(self, interaction: discord.Interaction, usuario: discord.Member, valor: int):
        if not is_adm(interaction):
            await interaction.response.send_message("Apenas ADMs podem usar este comando.", ephemeral=True)
            return

        if valor < 1:
            await interaction.response.send_message("O valor deve ser pelo menos 1.", ephemeral=True)
            return

        data = load()
        uid = str(usuario.id)

        if uid not in data:
            await interaction.response.send_message("Ficha não encontrada.", ephemeral=True)
            return

        data[uid]["max_hits"] = valor
        save(data)
        await interaction.response.send_message(f"💥 Máximo de acertos para **{data[uid]['nome']}** definido para `{valor}`.")

async def setup(bot):
    await bot.add_cog(Admin(bot))