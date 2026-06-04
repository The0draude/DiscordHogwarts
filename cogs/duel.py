import json
import os
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

from .combat_system import combat_system, SPELL_TYPES, SPELL_DESCRIPTIONS

DATA_PATH = "data/players.json"


def load_players():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_max_hits_for_user(user_id: str) -> int:
    """Retorna o máximo de acertos antes de ser derrotado"""
    data = load_players()
    user_id = str(user_id)
    if user_id not in data:
        return 3
    return data[user_id].get("max_hits", 3)


class SpellSelectView(View):
    """Select para escolher feitiço"""

    def __init__(self, duel_id: str, user_id: str, available_spells: list, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.duel_id = duel_id
        self.user_id = str(user_id)
        self.selected_spell = None

        options = []
        for spell in available_spells:
            emoji, spell_type = SPELL_DESCRIPTIONS.get(spell, ("❓", "Desconhecido"))
            options.append(
                discord.SelectOption(
                    label=spell,
                    value=spell,
                    description=f"({spell_type})",
                    emoji=emoji
                )
            )

        select = discord.ui.Select(
            placeholder="Escolha um feitiço...",
            min_values=1,
            max_values=1,
            options=options
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        spell = interaction.data["values"][0]
        self.selected_spell = spell

        # Verificar se é a ação do jogador correto
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ Este menu não é para você!",
                ephemeral=True
            )
            return

        # Atualizar ação no sistema
        both_ready = combat_system.set_action(self.duel_id, self.user_id, spell)
        duel = combat_system.get_duel(self.duel_id)
        
        if not duel:
            await interaction.response.send_message(
                "❌ Duelo não encontrado!",
                ephemeral=True
            )
            return

        emoji, spell_type = SPELL_DESCRIPTIONS.get(spell, ("❓", "Desconhecido"))

        if both_ready:
            # Ambos prontos, executar o turno
            await interaction.response.defer()
            
            max_hits_p1 = get_max_hits_for_user(duel.p1.user_id)
            max_hits_p2 = get_max_hits_for_user(duel.p2.user_id)
            max_hits = max(max_hits_p1, max_hits_p2)
            
            # Guardar turn_count antes de executar
            current_turn = duel.turn_count

            result, winner, duel_ended = combat_system.execute_round(self.duel_id, max_hits)

            # Reduzir cooldowns após o turno
            combat_system.reduce_cooldowns(self.duel_id)
            
            # Recuperar duel atualizado
            duel = combat_system.get_duel(self.duel_id)

            # Mensagem do resultado
            embed = discord.Embed(
                title=f"⚔️ Turno {current_turn + 1}",
                description=result,
                color=discord.Color.orange()
            )

            # Status atual
            status = f"<@{duel.p1.user_id}>: {duel.p1.hits}/{max_hits_p1} | <@{duel.p2.user_id}>: {duel.p2.hits}/{max_hits_p2}"
            embed.add_field(name="Status", value=status, inline=False)

            await interaction.followup.send(embed=embed)

            if duel_ended:
                # Duelo terminou
                if winner == duel.p1.user_id:
                    winner_mention = f"<@{duel.p1.user_id}>"
                else:
                    winner_mention = f"<@{duel.p2.user_id}>"

                embed = discord.Embed(
                    title="🏆 DUELO FINALIZADO!",
                    description=f"**{winner_mention}** VENCEU!",
                    color=discord.Color.gold()
                )
                await interaction.followup.send(embed=embed)
                combat_system.end_duel(self.duel_id)
            else:
                # Próximo turno
                next_player = duel.p2.user_id if self.user_id == duel.p1.user_id else duel.p1.user_id
                await interaction.followup.send(
                    f"✨ Próximo turno! <@{next_player}> use `/agir`"
                )
        else:
            # Aguardando o outro jogador
            await interaction.response.send_message(
                f"✅ {emoji} Você escolheu **{spell}**! Aguardando o oponente...",
                ephemeral=True
            )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="duelar",
        description="Inicia um duelo contra outro membro"
    )
    async def duelar(self, interaction: discord.Interaction, adversario: discord.Member):
        if adversario == interaction.user:
            await interaction.response.send_message(
                "Você não pode duelar consigo mesmo.",
                ephemeral=True
            )
            return

        if adversario.bot:
            await interaction.response.send_message(
                "Você não pode duelar um bot.",
                ephemeral=True
            )
            return

        data = load_players()
        p1_id = str(interaction.user.id)
        p2_id = str(adversario.id)

        if p1_id not in data or p2_id not in data:
            await interaction.response.send_message(
                "Ambos precisam ter ficha criada para duelar.",
                ephemeral=True
            )
            return

        # Verificar se já está em duelo
        result = combat_system.get_duel_by_user(p1_id)
        if result:
            await interaction.response.send_message(
                "Você já está em um duelo!",
                ephemeral=True
            )
            return

        result = combat_system.get_duel_by_user(p2_id)
        if result:
            await interaction.response.send_message(
                "O adversário já está em um duelo!",
                ephemeral=True
            )
            return

        # Criar duelo
        duel_id = combat_system.create_duel(p1_id, p2_id)
        duel = combat_system.get_duel(duel_id)

        max_hits_p1 = get_max_hits_for_user(p1_id)
        max_hits_p2 = get_max_hits_for_user(p2_id)

        embed = discord.Embed(
            title="⚔️ DESAFIO DE DUELO!",
            description=f"{interaction.user.mention} desafia {adversario.mention}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Configurações",
            value=f"**{interaction.user.display_name}**: {max_hits_p1} acertos\n**{adversario.display_name}**: {max_hits_p2} acertos",
            inline=False
        )
        embed.add_field(
            name="Como jogar",
            value="Use `/agir` para escolher um feitiço a cada turno",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        await interaction.followup.send(
            f"✨ {interaction.user.mention}, use `/agir` para começar!"
        )

    @app_commands.command(
        name="agir",
        description="Escolha um feitiço para o seu turno no duelo"
    )
    async def agir(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Encontrar duelo do usuário
        result = combat_system.get_duel_by_user(user_id)
        if not result:
            await interaction.response.send_message(
                "Você não está em um duelo ativo.",
                ephemeral=True
            )
            return

        duel_id, duel = result
        data = load_players()

        # Verificar se é a vez do jogador (verificar se já agiu neste turno)
        actions = combat_system.pending_actions.get(duel_id, {})
        if user_id == duel.p1.user_id and actions.get("p1") is not None:
            await interaction.response.send_message(
                "Você já agiu neste turno!",
                ephemeral=True
            )
            return
        if user_id == duel.p2.user_id and actions.get("p2") is not None:
            await interaction.response.send_message(
                "Você já agiu neste turno!",
                ephemeral=True
            )
            return

        # Feitiços desbloqueados
        available_spells = [
            spell for spell, info in data[user_id]["feiticos"].items()
            if info.get("desbloqueado", False)
        ]

        if not available_spells:
            await interaction.response.send_message(
                "Você não tem nenhum feitiço desbloqueado!",
                ephemeral=True
            )
            return

        # Filtrar por cooldown
        available = []
        for spell in available_spells:
            cooldown = combat_system.get_cooldown(duel_id, user_id, spell)
            if cooldown == 0:
                available.append(spell)

        if not available:
            on_cooldown = [f"{s} ({combat_system.get_cooldown(duel_id, user_id, s)} turnos)" for s in available_spells]
            await interaction.response.send_message(
                f"Todos seus feitiços estão em cooldown:\n" + "\n".join(on_cooldown),
                ephemeral=True
            )
            return

        # Mostrar select
        view = SpellSelectView(duel_id, user_id, available, timeout=120)
        await interaction.response.send_message(
            f"Escolha seu feitiço para o turno {duel.turn_count + 1}:",
            view=view,
            ephemeral=True
        )

    @app_commands.command(
        name="duelo-status",
        description="Mostra o status do duelo atual"
    )
    async def duelo_status(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        result = combat_system.get_duel_by_user(user_id)
        if not result:
            await interaction.response.send_message(
                "Você não está em um duelo ativo.",
                ephemeral=True
            )
            return

        duel_id, duel = result
        max_hits_p1 = get_max_hits_for_user(duel.p1.user_id)
        max_hits_p2 = get_max_hits_for_user(duel.p2.user_id)

        embed = discord.Embed(
            title=f"⚔️ Status do Duelo (Turno {duel.turn_count})",
            color=discord.Color.blue()
        )

        p1_status = f"<@{duel.p1.user_id}>\n**Acertos**: {duel.p1.hits}/{max_hits_p1}"
        if duel.p1.extra_turn:
            p1_status += "\n✨ Turno extra!"
        embed.add_field(name="Jogador 1", value=p1_status, inline=True)

        p2_status = f"<@{duel.p2.user_id}>\n**Acertos**: {duel.p2.hits}/{max_hits_p2}"
        if duel.p2.extra_turn:
            p2_status += "\n✨ Turno extra!"
        embed.add_field(name="Jogador 2", value=p2_status, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="sair-duelo",
        description="Sai do duelo atual (rende-se)"
    )
    async def sair_duelo(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        result = combat_system.get_duel_by_user(user_id)
        if not result:
            await interaction.response.send_message(
                "Você não está em um duelo ativo.",
                ephemeral=True
            )
            return

        duel_id, duel = result

        # Determinar o vencedor (o outro jogador)
        if user_id == duel.p1.user_id:
            winner_id = duel.p2.user_id
            loser_mention = interaction.user.mention
            winner_mention = f"<@{winner_id}>"
        else:
            winner_id = duel.p1.user_id
            loser_mention = interaction.user.mention
            winner_mention = f"<@{winner_id}>"

        embed = discord.Embed(
            title="⚔️ Duelo Abandonado",
            description=f"{loser_mention} se rendeu!\n\n🏆 {winner_mention} VENCEU!",
            color=discord.Color.gold()
        )

        await interaction.response.send_message(embed=embed)
        combat_system.end_duel(duel_id)


async def setup(bot):
    await bot.add_cog(Duel(bot))