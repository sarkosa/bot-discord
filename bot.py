from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import server  # Asegúrate de tener el módulo server configurado correctamente

load_dotenv()

TOKEN = os.environ["token"]

intents = discord.Intents.default()
intents.message_content = True  # Necesario para acceder al contenido de los mensajes
bot = commands.Bot(command_prefix='/', intents=intents)

# Define una variable global para el contador de mensajes
contador_mensajes = 0

# Define el comando de aplicación /nombre
@bot.tree.command(name="nombre", description="Muestra el nombre del usuario que ejecuta el comando")
async def nombre(interaction: discord.Interaction):
    # Obtiene el nombre del usuario que ejecuta el comando
    nombre = interaction.user.display_name
    # Responde al usuario con su nombre
    await interaction.response.send_message(f"Tu nombre es {nombre}")

# Comando para borrar mensajes
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
    amount = min(amount, 20)  # Limita el borrado a 20 mensajes

    # Envía una respuesta rápida para evitar el error de "Unknown interaction"
    await interaction.response.send_message(f"Intentando borrar {amount} mensajes...", ephemeral=True)

    # Borra los mensajes
    deleted = await interaction.channel.purge(limit=amount)
    # Envía un mensaje confirmando cuántos mensajes fueron borrados
    await interaction.followup.send(f"{len(deleted)} mensajes borrados.", ephemeral=True)

# Evento que se activa cuando se envía un mensaje
@bot.event
async def on_message(message):
    global contador_mensajes  # Usa la variable global para el contador

    # Evita que el bot responda a sí mismo
    if message.author == bot.user:
        return

    # Verifica si el mensaje es de un usuario específico y contiene un enlace de Tenor
    if message.author.id == 272731922717736971 and message.content.startswith("https://tenor.com/"):
        # Incrementa el contador
        contador_mensajes += 1
        # Envía el mensaje predeterminado junto con el contador
        await message.channel.send(f"ELPIEDRA se tocó el pilín {contador_mensajes} veces! 💦🤤💦")

    # Permite que otros comandos y eventos funcionen
    await bot.process_commands(message)



async def register_commands():
    await bot.tree.sync()

@bot.event
async def on_ready():
    await register_commands()
    print(f'Bot conectado como {bot.user}')

# Mantiene el bot en funcionamiento (por ejemplo, en Repl.it)
server.keep_alive()

# Ejecuta el bot con tu token
bot.run(TOKEN)
