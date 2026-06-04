import json
import os
from enum import Enum
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

DATA_PATH = "data/players.json"


class ActionType(Enum):
    ATTACK = "ataque"
    DEFENSE = "defesa"
    CONTROL = "controle"


# Mapping de feitiços para tipos de ação
SPELL_TYPES = {
    "expelliarmus": ActionType.DEFENSE,
    "stupefy": ActionType.ATTACK,
    "protego": ActionType.DEFENSE,
    "flipendo": ActionType.ATTACK,
    "reducto": ActionType.ATTACK,
    "sectumsempra": ActionType.ATTACK,
    "crucio": ActionType.CONTROL,
    "avada_kedavra": ActionType.ATTACK,
}

SPELL_DESCRIPTIONS = {
    "expelliarmus": ("🗡️ Expelliarmus", "Defesa"),
    "stupefy": ("⭐ Stupefy", "Ataque"),
    "protego": ("🛡️ Protego", "Defesa"),
    "flipendo": ("👊 Flipendo", "Ataque"),
    "reducto": ("💥 Reducto", "Ataque"),
    "sectumsempra": ("🔪 Sectumsempra", "Ataque"),
    "crucio": ("🌪️ Crucio", "Controle"),
    "avada_kedavra": ("☠️ Avada Kedavra", "Ataque (ignora Defesa!)"),
}


@dataclass
class PlayerDuelState:
    """Estado individual de um jogador no duelo"""
    user_id: str
    hits: int = 0
    cooldowns: Dict[str, int] = field(default_factory=dict)
    extra_turn: bool = False
    last_action: Optional[ActionType] = None
    last_spell: Optional[str] = None

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "hits": self.hits,
            "cooldowns": self.cooldowns,
            "extra_turn": self.extra_turn,
            "last_action": self.last_action.value if self.last_action else None,
            "last_spell": self.last_spell,
        }

    @staticmethod
    def from_dict(data):
        state = PlayerDuelState(
            user_id=data["user_id"],
            hits=data.get("hits", 0),
            cooldowns=data.get("cooldowns", {}),
            extra_turn=data.get("extra_turn", False),
            last_action=ActionType(data["last_action"]) if data.get("last_action") else None,
            last_spell=data.get("last_spell"),
        )
        return state


@dataclass
class DuelState:
    """Estado completo de um duelo"""
    duel_id: str
    p1: PlayerDuelState
    p2: PlayerDuelState
    turn_count: int = 0
    history: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))

    def to_dict(self):
        return {
            "duel_id": self.duel_id,
            "p1": self.p1.to_dict(),
            "p2": self.p2.to_dict(),
            "turn_count": self.turn_count,
            "history": self.history,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @staticmethod
    def from_dict(data):
        state = DuelState(
            duel_id=data["duel_id"],
            p1=PlayerDuelState.from_dict(data["p1"]),
            p2=PlayerDuelState.from_dict(data["p2"]),
            turn_count=data.get("turn_count", 0),
            history=data.get("history", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            expires_at=datetime.fromisoformat(data.get("expires_at", (datetime.now() + timedelta(hours=1)).isoformat())),
        )
        return state


class CombatSystem:
    def __init__(self):
        self.duels: Dict[str, DuelState] = {}
        self.pending_actions: Dict[str, Dict] = {}

    def create_duel(self, p1_id: str, p2_id: str) -> str:
        """Cria um novo duelo"""
        duel_id = f"{p1_id}_vs_{p2_id}_{int(datetime.now().timestamp() * 1000)}"
        self.duels[duel_id] = DuelState(
            duel_id=duel_id,
            p1=PlayerDuelState(user_id=p1_id),
            p2=PlayerDuelState(user_id=p2_id),
        )
        self.pending_actions[duel_id] = {"p1": None, "p2": None}
        return duel_id

    def get_duel(self, duel_id: str) -> Optional[DuelState]:
        if duel_id in self.duels:
            duel = self.duels[duel_id]
            if duel.expires_at < datetime.now():
                del self.duels[duel_id]
                return None
            return duel
        return None

    def get_duel_by_user(self, user_id: str) -> Optional[Tuple[str, DuelState]]:
        """Encontra um duelo do usuário"""
        for duel_id, duel in self.duels.items():
            if duel.expires_at >= datetime.now():
                if user_id == duel.p1.user_id or user_id == duel.p2.user_id:
                    return (duel_id, duel)
            else:
                del self.duels[duel_id]
        return None

    def set_action(self, duel_id: str, user_id: str, spell: str) -> bool:
        """Define a ação de um jogador. Retorna True se ambos estão prontos."""
        duel = self.get_duel(duel_id)
        if not duel:
            return False

        if user_id == duel.p1.user_id:
            self.pending_actions[duel_id]["p1"] = spell
        elif user_id == duel.p2.user_id:
            self.pending_actions[duel_id]["p2"] = spell
        else:
            return False

        return self.pending_actions[duel_id]["p1"] is not None and self.pending_actions[duel_id]["p2"] is not None

    def execute_round(self, duel_id: str, max_hits: int = 3) -> Tuple[str, Optional[str], bool]:
        """
        Executa um turno do duelo.
        Retorna: (mensagem, winner_id, duelo_terminou)
        """
        duel = self.get_duel(duel_id)
        if not duel:
            return "Duelo não encontrado.", None, True

        actions = self.pending_actions.get(duel_id, {})
        p1_spell = actions.get("p1")
        p2_spell = actions.get("p2")

        if not p1_spell or not p2_spell:
            return "Ambos os jogadores precisam escolher uma ação.", None, False

        p1_action = SPELL_TYPES.get(p1_spell, ActionType.ATTACK)
        p2_action = SPELL_TYPES.get(p2_spell, ActionType.ATTACK)

        result = self._resolve_turn(duel, p1_action, p2_action, p1_spell, p2_spell)

        duel.turn_count += 1
        duel.history.append(result)
        self.pending_actions[duel_id] = {"p1": None, "p2": None}

        winner = None
        if duel.p1.hits >= max_hits:
            winner = duel.p1.user_id
        elif duel.p2.hits >= max_hits:
            winner = duel.p2.user_id

        return result, winner, winner is not None

    def _resolve_turn(
        self,
        duel: DuelState,
        p1_action: ActionType,
        p2_action: ActionType,
        p1_spell: str,
        p2_spell: str,
    ) -> str:
        """Resolve o triângulo de combate"""
        lines = []

        if p1_action == p2_action:
            return self._resolve_tie(duel, p1_action, p1_spell, p2_spell)

        p1_avada = p1_spell.lower() == "avada_kedavra"
        p2_avada = p2_spell.lower() == "avada_kedavra"

        # Determinar quem vence
        p1_wins = (
            (p1_action == ActionType.ATTACK and p2_action == ActionType.CONTROL) or
            (p1_action == ActionType.CONTROL and p2_action == ActionType.DEFENSE) or
            (p1_action == ActionType.DEFENSE and p2_action == ActionType.ATTACK) or
            (p1_avada and p2_action == ActionType.DEFENSE)
        )

        if p1_wins:
            lines.append(f"⚔️ **{duel.p1.user_id}** lançou **{p1_spell}**!")
            lines.append(f"❌ **{duel.p2.user_id}** com **{p2_spell}** não conseguiu se defender!")
            
            if p1_action == ActionType.DEFENSE and p2_action == ActionType.ATTACK:
                lines.append(f"✨ Bloqueio perfeito! **{duel.p1.user_id}** ganha turno extra!")
                duel.p1.extra_turn = True
            else:
                duel.p1.hits += 1
                lines.append(f"✅ ACERTO! **{duel.p1.user_id}**: {duel.p1.hits} | **{duel.p2.user_id}**: {duel.p2.hits}")
        else:
            lines.append(f"⚔️ **{duel.p2.user_id}** lançou **{p2_spell}**!")
            lines.append(f"❌ **{duel.p1.user_id}** com **{p1_spell}** não conseguiu se defender!")
            
            if p2_action == ActionType.DEFENSE and p1_action == ActionType.ATTACK:
                lines.append(f"✨ Bloqueio perfeito! **{duel.p2.user_id}** ganha turno extra!")
                duel.p2.extra_turn = True
            else:
                duel.p2.hits += 1
                lines.append(f"✅ ACERTO! **{duel.p2.user_id}**: {duel.p2.hits} | **{duel.p1.user_id}**: {duel.p1.hits}")

        return "\n".join(lines)

    def _resolve_tie(
        self,
        duel: DuelState,
        action: ActionType,
        p1_spell: str,
        p2_spell: str,
    ) -> str:
        """Resolve empates"""
        lines = []

        if action == ActionType.ATTACK:
            lines.append(f"💥 Ambos atacam simultaneamente!")
            lines.append(f"  • **{duel.p1.user_id}** → {p1_spell}")
            lines.append(f"  • **{duel.p2.user_id}** → {p2_spell}")
            duel.p1.hits += 1
            duel.p2.hits += 1
            lines.append(f"⚡ TROCA DE DANO! Ambos levam acertos!")
            lines.append(f"  **{duel.p1.user_id}**: {duel.p1.hits} | **{duel.p2.user_id}**: {duel.p2.hits}")

        elif action == ActionType.DEFENSE:
            lines.append(f"🛡️ Ambos se defendem mutuamente!")
            lines.append(f"  • **{duel.p1.user_id}** → {p1_spell}")
            lines.append(f"  • **{duel.p2.user_id}** → {p2_spell}")
            lines.append(f"⏳ Nada acontece... Turno perdido!")

        elif action == ActionType.CONTROL:
            lines.append(f"🌪️ Ambos lançam controle!")
            lines.append(f"  • **{duel.p1.user_id}** → {p1_spell}")
            lines.append(f"  • **{duel.p2.user_id}** → {p2_spell}")
            lines.append(f"✨ Debuffs neutralizam-se... (puro roleplay!)")

        return "\n".join(lines)

    def add_cooldown(self, duel_id: str, user_id: str, spell: str, turns: int = 2):
        """Adiciona cooldown a um feitiço"""
        duel = self.get_duel(duel_id)
        if not duel:
            return

        if user_id == duel.p1.user_id:
            duel.p1.cooldowns[spell] = turns
        elif user_id == duel.p2.user_id:
            duel.p2.cooldowns[spell] = turns

    def get_cooldown(self, duel_id: str, user_id: str, spell: str) -> int:
        """Retorna cooldown de um feitiço (0 = pronto)"""
        duel = self.get_duel(duel_id)
        if not duel:
            return 0

        if user_id == duel.p1.user_id:
            return duel.p1.cooldowns.get(spell, 0)
        else:
            return duel.p2.cooldowns.get(spell, 0)

    def reduce_cooldowns(self, duel_id: str):
        """Reduz cooldowns após um turno"""
        duel = self.get_duel(duel_id)
        if not duel:
            return

        for spell in duel.p1.cooldowns:
            duel.p1.cooldowns[spell] = max(0, duel.p1.cooldowns[spell] - 1)
        for spell in duel.p2.cooldowns:
            duel.p2.cooldowns[spell] = max(0, duel.p2.cooldowns[spell] - 1)

    def end_duel(self, duel_id: str):
        """Finaliza um duelo"""
        if duel_id in self.duels:
            del self.duels[duel_id]
        if duel_id in self.pending_actions:
            del self.pending_actions[duel_id]


combat_system = CombatSystem()
