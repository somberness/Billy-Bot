import discord
import requests
import json
import os
from discord.client import Client
from discord.ext import commands 
from discord.guild import Guild
from discord.guild import GroupChannel
from discord.channel import TextChannel

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open('config.json') as config_file:
    config = json.load(config_file)
    DISCORD_TOKEN = config["discord_bot_token"]
    HYPIXEL_API_KEY = config["api_key"]

intents = discord.Intents.all()
intents.presences = True 
intents.members = True
intents.guilds =True
client = commands.Bot(command_prefix='.', intents=intents)
prefix = '.'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    guild = client.get_guild(1254537289514749983)
    channel = guild.get_channel(1254537547426562198)
    embed=discord.Embed(description=f'Bot status:\n ONLINE', color=discord.Color.red())
    await channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        print(f'Received message from {message.author}: {message.content}')
    
    if message.content.startswith(f'{prefix}ping'):
            embed=discord.Embed(description=f"Pong! I responded in {float(round(client.latency * 100))} ms. Ain't that impressive!", color=discord.Color.magenta())
            await message.channel.send(embed=embed)
    

client.run(DISCORD_TOKEN)