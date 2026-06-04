import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def pegar_ou_criar_categoria(guild, nome):
    categoria = discord.utils.get(guild.categories, name=nome)
    if categoria:
        print(f"📂 Categoria já existe: {nome}")
    else:
        categoria = await guild.create_category(nome)
        print(f"✅ Categoria criada: {nome}")
    return categoria


@bot.command(name="Criar")
async def criar_texto(ctx, nome_categoria: str, canais_str: str):
    guild = ctx.guild
    canais = [c.strip() for c in canais_str.split(",")]

    print("─" * 40)
    print(f"🏠 Servidor: {guild.name}")
    print(f"📂 Categoria: {nome_categoria}")
    print(f"📋 Canais a criar: {canais}")
    print("─" * 40)

    categoria = await pegar_ou_criar_categoria(guild, nome_categoria)

    for nome_canal in canais:
        try:
            canal = await guild.create_text_channel(nome_canal, category=categoria)
            print(f"  ✓ Texto criado: #{canal.name}")
            await asyncio.sleep(0.3)
        except discord.HTTPException as e:
            print(f"  ✗ Erro ao criar #{nome_canal}: {e}")

    print("─" * 40)
    print("✅ Concluído!")


@bot.command(name="CriarPostagem")
async def criar_postagem(ctx, nome_categoria: str, canais_str: str):
    guild = ctx.guild
    canais = [c.strip() for c in canais_str.split(",")]

    print("─" * 40)
    print(f"🏠 Servidor: {guild.name}")
    print(f"📂 Categoria: {nome_categoria}")
    print(f"📋 Canais de postagem a criar: {canais}")
    print("─" * 40)

    categoria = await pegar_ou_criar_categoria(guild, nome_categoria)

    for nome_canal in canais:
        try:
            canal = await guild.create_forum(nome_canal, category=categoria)
            print(f"  ✓ Postagem criada: #{canal.name}")
            await asyncio.sleep(0.3)
        except discord.HTTPException as e:
            print(f"  ✗ Erro ao criar #{nome_canal}: {e}")

    print("─" * 40)
    print("✅ Concluído!")


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print("Aguardando comandos...")
    print("─" * 40)


bot.run(TOKEN)