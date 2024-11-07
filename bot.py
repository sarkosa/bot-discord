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
AUDIO_URL = "https://github.com/sarkosa/bot-discord/raw/refs/heads/main/Mosquito%20-%20Sound%20Effect%20%5BHQ%5D.mp3"

# ID del canal de voz específico al que deseas que se conecte el bot
VOICE_CHANNEL_ID = 877819520792813579

# Define una variable global para el contador de mensajes y el volumen
contador_mensajes = 4
volume = 3.0  # Valor inicial del volumen (0.5 = 50%)

# Función para descargar el archivo de audio desde GitHub
def download_audio():
    response = requests.get(AUDIO_URL)
    with open("sonido.mp3", "wb") as f:
        f.write(response.content)

# Llama a la función para descargar el archivo al iniciar el bot
@bot.event
async def on_ready():
    download_audio()  # Descargar el archivo de audio desde GitHub
    random_sound_task.start()  # Inicia la tarea para reproducir sonido cada 30 minutos
    await bot.tree.sync()
    print(f'Bot conectado como {bot.user}')

# Comando para ajustar el volumen
@bot.tree.command(name="setvolume", description="Ajusta el volumen de reproducción entre 0 y 100.")
async def set_volume(interaction: discord.Interaction, vol: int):
    global volume
    # Limita el valor del volumen entre 0 y 100
    if 0 <= vol <= 100:
        volume = vol / 100  # Convierte el valor a un rango de 0.0 a 1.0
        await interaction.response.send_message(f"Volumen ajustado a {vol}%.")
    else:
        await interaction.response.send_message("Por favor ingresa un valor entre 0 y 100.", ephemeral=True)

# Función que reproduce sonido en el canal de voz específico usando el ID
async def play_sound_in_specific_voice_channel():
    for guild in bot.guilds:
        voice_channel = guild.get_channel(VOICE_CHANNEL_ID)

        if voice_channel:
            # Si el bot ya está conectado a un canal de voz, desconéctalo primero
            if voice_channel.guild.voice_client:
                await voice_channel.guild.voice_client.disconnect()

            # Conectarse y reproducir el audio
            vc = await voice_channel.connect()
            source = discord.FFmpegPCMAudio("sonido.mp3", options=f"-filter:a 'volume={volume}'")
            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

            await vc.disconnect()
            break

# Tarea que ejecuta el sonido cada 30 minutos
@tasks.loop(minutes=3)
async def random_sound_task():
    await play_sound_in_specific_voice_channel()

# Define el comando de aplicación /nombre
@bot.tree.command(name="nombre", description="Muestra el nombre del usuario que ejecuta el comando")
async def nombre(interaction: discord.Interaction):
    nombre = interaction.user.display_name
    await interaction.response.send_message(f"Tu nombre es {nombre}")

# Comando para borrar mensajes
@bot.tree.command(name="clear", description="Borra un número especificado de mensajes del canal.")
async def clear(interaction: discord.Interaction, amount: int):
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Este comando solo se puede usar en servidores.", ephemeral=True)
        return

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("No tienes permisos para borrar mensajes.", ephemeral=True)
        return

    amount = min(amount, 20)
    await interaction.response.send_message(f"Intentando borrar {amount} mensajes...", ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"{len(deleted)} mensajes borrados.", ephemeral=True)

# Evento que se activa cuando se envía un mensaje
@bot.event
async def on_message(message):
    global contador_mensajes

    if message.author == bot.user:
        return
    
    # Verifica si el mensaje contiene "bz" y si el mensaje es en el canal específico
    if "bz" in message.content.lower() and message.channel.id == 877810069239136268:
        # Intenta unirse al canal de voz y reproducir el sonido
        await play_sound_in_specific_voice_channel()

    # Verifica los mensajes de ELPIEDRA
    if message.author.id == 272731922717736971 and message.content.startswith("https://tenor.com/"):
        contador_mensajes += 1
        await message.channel.send(f"ELPIEDRA se tocó el pilín {contador_mensajes} veces! 💦🤤💦")

    await bot.process_commands(message)

# Mantiene el bot en funcionamiento (por ejemplo, en Repl.it)
server.keep_alive()

# Ejecuta el bot con tu token
bot.run(TOKEN)
