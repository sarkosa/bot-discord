from dotenv import load_dotenv
import os
import discord
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


@bot.tree.command(name="clear", description="Borra un número especificado de mensajes del canal.")
async def clear(interaction: discord.Interaction, amount: int):
    # Verifica si el comando fue ejecutado en un canal de texto
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Este comando solo se puede usar en servidores.", ephemeral=True)
        return

    # Verifica que el usuario que ejecuta el comando tenga permisos de administrador
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("No tienes permisos para borrar mensajes.", ephemeral=True)
        return

    # Limita el número de mensajes a borrar
    amount = min(amount, 5)  # Discord limita a borrar hasta 100 mensajes a la vez

    # Envía una respuesta rápida para evitar el error de "Unknown interaction"
    await interaction.response.send_message(f"Intentando borrar {amount} mensajes...", ephemeral=True)
    
    # Borra los mensajes
    deleted = await interaction.channel.purge(limit=amount)
     # Envía un mensaje confirmando cuántos mensajes fueron borrados
    await interaction.followup.send(f"{len(deleted)} mensajes borrados.", ephemeral=True)


async def register_commands():
    await bot.tree.sync()

@bot.event
async def on_ready():
    await register_commands()
    print(f'Bot conectado como {bot.user}')

server.keep_alive()

# Ejecuta el bot con tu token
bot.run(TOKEN)
