import requests
import os
import youtube_dl

import discord
from dotenv import load_dotenv
from discord.ext import commands,tasks

# ----------------------------------------------------------------------------------------------
# WEBHOOK METHOD
def testWebHook(value):
	# Webhook of my channel. Click on edit channel --> Webhooks --> Creates webhook
	mUrl = ""

	data = {"content": value}
	response = requests.post(mUrl, json=data)

# CALLBACK RECURSIVE METHOD TO PLAY NEXT AUDIO URL
def play_next(ctx):
	# if queue is NOT empty
	if not not queue:
		os.remove(queue[0])
		del queue[0]

	# if queue is NOT empty
	if not not queue:
		print(len(queue), queue)

		server = ctx.message.guild
		voice_channel = server.voice_client

		testWebHook("Playing next item in queue - " + queue[0])

		# ffmpeg must be installed in C:\ffmpeg\bin and defined in windows environment variables
		voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=queue[0]), after=lambda e: play_next(ctx))
	else:
		testWebHook("The bot has no remaining items in queue.")

# ----------------------------------------------------------------------------------------------
# YOUTUBE_DL CONFIG

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = ""

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]
		filename = data['title'] if stream else ytdl.prepare_filename(data)
		return filename
# ----------------------------------------------------------------------------------------------

# PROGRAM INIT CODE
load_dotenv()
TOKEN = ''

queue = []
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

# BOT ON READY MESSAGE
@bot.event
async def on_ready():
	testWebHook("DJGoatBot is connected.")

# ------------------------------------------------------------------------------

# COMMAND THE BOT TO LEAVE VOICE CHANNEL OF MESSAGE AUTHOR
@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
	voice_client = ctx.message.guild.voice_client
	if voice_client.is_connected():
		await voice_client.disconnect()
	else:
		testWebHook("The bot is not connected to a voice channel.")

# COMMAND THE BOT TO JOIN VOICE CHANNEL OF MESSAGE AUTHOR
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
	if not ctx.message.author.voice:
		await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
		return
	else:
		channel = ctx.message.author.voice.channel
	await channel.connect()

# COMMAND THE BOT TO PLAY AUDIO OF PASSED URL
@bot.command(name='play', help='To play song')
async def play(ctx,url):
	try :
		# logic to check if bot is playing an audio file, otherwise download the audio file via youtube_dl and play it in voice channel
		server = ctx.message.guild
		voice_channel = server.voice_client

		testWebHook("Initiated URL download...")
		filename = await YTDLSource.from_url(url, loop=bot.loop)
		queue.append(filename)
		if ctx.voice_client.is_playing():
			# BUILD QUEUE LOGIC
			testWebHook("The bot is already playing. URL has been added to queue.")
		else:
			# CALLBACK 'AFTER' LAMBDA METHOD TO PLAY NEXT SONG
			voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=queue[0]), after=lambda e: play_next(ctx))
			testWebHook("Download complete. Now playing - {}".format(queue[0]))
		
	except:
		for i in queue:
			os.remove(i)
		queue.clear()
		testWebHook("The bot is not connected to a voice channel.")

# COMMAND THE BOT TO PAUSE CURRENT ITEM IN PLAYER
@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
	voice_client = ctx.message.guild.voice_client
	if voice_client.is_playing():
		await voice_client.pause()
		testWebHook("The bot has been paused.")
	else:
		testWebHook("The bot is not playing anything at the moment.")

# COMMAND THE BOT TO RESUME CURRENT ITEM IN PLAYER
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
	voice_client = ctx.message.guild.voice_client
	if voice_client.is_paused():
		await voice_client.resume()
		testWebHook("The bot has been resumed.")
	else:
		testWebHook("The bot was not playing anything before this. Use !play command")

# COMMAND THE BOT TO STOP CURRENT ITEM IN PLAYER
@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
	voice_client = ctx.message.guild.voice_client
	if voice_client.is_playing():
		await voice_client.stop()
		testWebHook("The bot has been skipped.")
	else:
		testWebHook("The bot is not playing anything at the moment.")

# COMMAND TO THE BOT TO CLEAR ALL ITEMS IN PLAYER QUEUE
#@bot.command(name='clear', help='Clears queue')
#async def clear(ctx):
#	voice_client = ctx.message.guild.voice_client
#	if voice_client.is_playing():
#		await voice_client.stop()
#		testWebHook("The bot has been stopped.")
#	else:
#		testWebHook("The bot is not playing anything at the moment.")

# COMMAND THE BOT TO SHOW THE LIST OF AVAILABLE COMMANDS
@bot.command(name='commands', help='To reply back with all bot commands')
async def commands(ctx):
	testWebHook("# !clear - [DISABLED] command the bot to clear out all items in player queue and stops player.\n# !stop - commands the bot to stop the current item in player queue and moves to next.\n# !resume - command the bot to resume paused item being played from player queue.\n# !pause - command the bot to pause the item being played from player queue.\n# !play - command the bot to play audio from a URL parameter passed.\n# !join - command the bot to join voice channel of message author.\n# !leave - command the bot to leave voice channel of message author.\n# !list - command the bot to print all items in player queue.")

# COMMAND THE BOT TO SHOW LIST OF ITEMS IN PLAYER QUEUE
@bot.command(name='list', help='To view all queued player items')
async def list(ctx):
	testWebHook(str(queue).replace(',', '\n'))
# ------------------------------------------------------------------------------

bot.run(TOKEN)
