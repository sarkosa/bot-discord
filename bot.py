from dotenv import load_dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
import server

load_dotenv()

TOKEN = os.environ["token"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Define el comando de aplicación /nombre
@bot.tree.command(name="nombre", description="Muestra el nombre del usuario que ejecuta el comando")
async def nombre(interaction: discord.Interaction):

    # Obtiene el nombre del usuario que ejecuta el comando
    nombre = interaction.user.display_name

    # Responde al usuario con su nombre
    await interaction.response.send_message(f"Tu nombre es {nombre}")

async def register_commands():
    await bot.tree.sync()

@bot.event
async def on_ready():
    await register_commands()
    print(f'Bot conectado como {bot.user}')

server.keep_alive()

# Ejecuta el bot con tu token
bot.run(TOKEN)
