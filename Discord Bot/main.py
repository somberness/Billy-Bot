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

    if message.content.startswith(f'{prefix}hypixel'):
        # Extract the Minecraft username from the message
        username = message.content.split(' ')[1]
        # Fetch UUID from Mojang API
        mojang_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
        if mojang_response.status_code == 200:
            uuid = mojang_response.json()['id']
            await message.channel.send(f'{username}s user id is {uuid}')
        else:
            await message.channel.send(f'Could not find player {username}')
            return

        # Fetch player data from Hypixel API
        hypixel_response = requests.get(f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
        if hypixel_response.status_code == 200 and hypixel_response.json()['success']:
            player_data = hypixel_response.json()['player']
            player_name = player_data['displayname']
            player_rank = player_data.get('rank', 'No rank')
            player_network_level = player_data.get('networkLevel', 0)
            
            response_message = (
                f"Player: {player_name}\n"
                f"Rank: {player_rank}\n"
                f"Network Level: {player_network_level}\n"
            )
            await message.channel.send(response_message)
        else:
            await message.channel.send(f'Could not fetch data for player {username}')
    

client.run(DISCORD_TOKEN)
