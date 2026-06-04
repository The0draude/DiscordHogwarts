import discord
from discord.ext import commands
import asyncio

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
TOKEN = "SEU_TOKEN_AQUI"

# IDs de canais que você quer PRESERVAR (deixe vazio para deletar tudo)
CANAIS_PRESERVAR = set()
# Exemplo: CANAIS_PRESERVAR = {123456789, 987654321}

# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print("─" * 40)

    for guild in bot.guilds:
        print(f"🏠 Servidor: {guild.name} ({guild.id})")
        print(f"📋 Total de canais: {len(guild.channels)}")

        canais = [c for c in guild.channels if c.id not in CANAIS_PRESERVAR]
        print(f"🗑️  Canais a deletar: {len(canais)}")
        print("─" * 40)

        deletados = 0
        erros = 0

        for canal in canais:
            try:
                await canal.delete(reason="Limpeza pós-raid")
                print(f"  ✓ Deletado: #{canal.name} ({type(canal).__name__})")
                deletados += 1
                await asyncio.sleep(0.5)  # Evita rate limit
            except discord.Forbidden:
                print(f"  ✗ Sem permissão: #{canal.name}")
                erros += 1
            except discord.HTTPException as e:
                print(f"  ✗ Erro HTTP em #{canal.name}: {e}")
                erros += 1

        print("─" * 40)
        print(f"✅ Deletados: {deletados}")
        print(f"❌ Erros: {erros}")
        print("Limpeza concluída!")

        # Cria um canal geral após a limpeza
        canal = await guild.create_text_channel("geral")
        print(f"✅ Canal criado: #{canal.name}")

    await bot.close()


bot.run(TOKEN)