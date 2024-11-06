from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
import asyncio
import server  # Asegúrate de tener el módulo server configurado correctamente
import requests  # Librería para descargar archivos desde internet

load_dotenv()

TOKEN = os.environ["token"]

intents = discord.Intents.default()
intents.message_content = True  # Necesario para acceder al contenido de los mensajes
bot = commands.Bot(command_prefix='/', intents=intents)

# URL del archivo de audio en tu repositorio de GitHub
AUDIO_URL = "https://github.com/sarkosa/bot-discord/raw/refs/heads/main/Mosquito%20-%20Sound%20Effect%20%5BHQ%5D.mp3"  # Reemplaza con la URL de tu archivo

# ID del canal de voz específico al que deseas que se conecte el bot
VOICE_CHANNEL_ID = 877819520792813579

# Define una variable global para el contador de mensajes
contador_mensajes = 4

# Función para descargar el archivo de audio desde GitHub
def download_audio():
    response = requests.get(AUDIO_URL)
    with open("sonido.mp3", "wb") as f:
        f.write(response.content)

# Llama a la función para descargar el archivo al iniciar el bot
@bot.event
async def on_ready():
    download_audio()  # Descargar el archivo de audio desde GitHub
    random_sound_task.start()  # Inicia la tarea para reproducir sonido cada hora
    await bot.tree.sync()
    print(f'Bot conectado como {bot.user}')

# Función que reproduce sonido en el canal de voz específico usando el ID
async def play_sound_in_specific_voice_channel():
    for guild in bot.guilds:
        voice_channel = guild.get_channel(VOICE_CHANNEL_ID)  # Obtén el canal de voz por ID

        if voice_channel:  # Asegúrate de que el canal existe
            vc = await voice_channel.connect()
            source = discord.FFmpegPCMAudio("sonido.mp3")
            vc.play(source)
            
            # Espera a que termine de reproducirse el sonido
            while vc.is_playing():
                await asyncio.sleep(1)
            
            # Desconecta del canal de voz
            await vc.disconnect()
            break

# Tarea que ejecuta el sonido una vez por hora
@tasks.loop(hours=1)
async def random_sound_task():
    await play_sound_in_specific_voice_channel()

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
        # Envía el mensaje pred
