import discord
import requests
import json
import os
from discord import user
from discord import colour
from discord.channel import VoiceChannel
from discord.client import Client
from discord.ext import commands 
from discord.guild import Guild
from discord.guild import GroupChannel
from discord.channel import TextChannel
from discord.member import *

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
mention = '<@1254540375851405352>'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    guild = client.get_guild(1254537289514749983)
    channel = guild.get_channel(1254537547426562198)
    embed=discord.Embed(description=f'Bot status:\n ONLINE', color=discord.Color.red())
    await channel.send(embed=embed)
    await client.change_presence(activity=discord.Game('Type .help!'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        print(f'Received message from {message.author}: {message.content}')
    
    #if bot is pinged
    if mention in message.content:
        await message.channel.send(
        f'Hello {message.author.mention}! My prefix is .\nUse .help for a list of commands!'
        )
    
    #.ping command
    if message.content.startswith(f'{prefix}ping'):
            embed=discord.Embed(description=f"Pong! I responded in {float(round(client.latency * 100))} ms. Ain't that impressive!", color=discord.Color.magenta())
            await message.channel.send(embed=embed)
    
    #.hypixel command
    if message.content.startswith(f'{prefix}hypixel'):
        username = message.content.split(' ')[1]
        # Fetch UUID from Mojang API
        mojang_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
        if mojang_response.status_code == 200:
            uuid = mojang_response.json()['id']
        else:
            await message.channel.send(f'Could not find player {username}')
            return

        # Fetch player data from Hypixel API
        hypixel_response = requests.get(f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
        if hypixel_response.status_code == 200 and hypixel_response.json()['success']:
            player_data = hypixel_response.json()['player']
            player_name = player_data['displayname']
            player_online = player_data.get('lastLogin') > player_data.get('lastLogout')  # Online if last login is after last logout
            player_rank = player_data.get('rank', player_data.get('newPackageRank', player_data.get('monthlyPackageRank', 'None')))
            player_rank_color = player_data.get('rankPlusColor', 'None')  # Default to 'None' if no color is found
            player_level = (player_data['networkExp'] / 10000) if 'networkExp' in player_data else 0  # Hypixel level is derived from network experience
            player_karma = player_data.get('karma', 0)

            embed = discord.Embed(title=f"{player_name}'s basic hypixel stats:", color=discord.Color.dark_orange())
            embed.add_field(name='Display name:', value=player_name, inline=True)
            embed.add_field(name='Online?', value='Yes' if player_online else 'No', inline=True)
            embed.add_field(name='Rank:',value=player_rank, inline=True)
            embed.add_field(name='Rank colour:', value=player_rank_color, inline=True)
            embed.add_field(name='Level:', value=player_level, inline=True)
            embed.add_field(name='Karma:', value=player_karma, inline=True)
            embed.set_footer(icon_url=message.author.avatar, text = f'Requested by {message.author.name}')

            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f'Could not fetch data for player {username}')
    
   #.help command
    if message.content.startswith(f'{prefix}help'):
            embed = discord.Embed(title='**Commands:**',
                                color=discord.Color.dark_green())
            embed.add_field(name='**.Help**',
                            value='Runs this command.',
                            inline=False)
            embed.add_field(name='**.ping**',
                            value='Returns the bot\'s latency.',
                            inline=False)
            embed.add_field(
                name='**.hypixel {Username}**',
                value='Returns Hypixel user stats, must include username.',
                inline=False)
            await message.channel.send(embed=embed)

    #DRILLY BILLY  
    if message.content.startswith(f'{prefix}drilly'):
            await message.channel.send(f'DRILLINGS')

client.run(DISCORD_TOKEN)
