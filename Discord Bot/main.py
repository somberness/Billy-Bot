#IMPORTS
import discord
import json
import os
import asyncio
import requests
from discord import colour, player
from discord import user
from discord.channel import TextChannel
from discord.channel import VoiceChannel
from discord.client import Client
from discord.ext import *
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.guild import *
from discord.member import *
from discord.message import *
from discord.utils import *
from discord.voice_client import VoiceClient
from discord import FFmpegPCMAudio
from discord import opus
from discord import FFmpegOpusAudio
import time
import random
import yt_dlp as youtube_dl
from collections import deque
import sys
import re
#SECRETS
#DISCORD_TOKEN = os.environ['discord_bot_token']
#HYPIXEL_API_KEY = os.environ['api_key']

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config
config = load_config('config.json')
DISCORD_TOKEN= config.get('discord_bot_token')
HYPIXEL_API_KEY = config.get('api_key')

#INTS AND ASSIGNING
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)
bot = client
prefix = '.'
mention = '<@1254540375851405352>'
bot.remove_command('help')

##--EVENTS--#


#ON READY LOGS
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(1254537547426562198)
    embed = discord.Embed(description=f'Bot status:\n ONLINE',
                          color=discord.Color.red())
    await channel.send(embed=embed)
    await client.change_presence(activity=discord.Game('Type .help!'))


#USER JOIN / LEAVE MESSAGE
@bot.event
async def on_member_join(member):
    channel = client.get_channel(1254537290110337036)
    await channel.send(
        f'Welcome, {member}!')


@bot.event
async def on_member_remove(member):
    channel = client.get_channel(1254537290110337036)
    await channel.send(f'Goodbye, {member}!')


#--COMMANDS--#


#help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(title='**Commands:**',
                          color=discord.Color.dark_green())
    embed.add_field(name='**.help**', value='Runs this command.', inline=False)
    embed.add_field(name='**.ping**',
                    value='Returns the bot\'s latency.',
                    inline=False)
    embed.add_field(name='**.hypixel**',
                    value='Returns Hypixel command help sheet.',
                    inline=False)
    embed.add_field(name='**.aristotle**',
                    value='Returns help sheet for aristotle quotes.',
                    inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def aristotle(ctx):
    embed = discord.Embed(title='**Commands:**',
                          color=discord.Color.dark_green())
    embed.add_field(name='**.quote_status**', value='Returns a value showing whether Aristotle is active or inactive.', inline=False)
    embed.add_field(name='**.quote_toggle True/False**',
                    value='Toggles Aristotle on or off. ',
                    inline=False)
    embed.add_field(name='**.quote_change_target {user ID}**',
                    value='Allows user to change the target of Aristotle, user must provide\n the user ID. e.g ".quote_change_target 971628298041970688".',
                    inline=False)
    embed.add_field(name='**.quote_target**',
                    value='Returns current Aristotle target.',
                    inline=False)
    embed.add_field(name='**.quote_reset**',
                    value='Resets current Aristotle target.',
                    inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def hypixel(ctx):
    embed = discord.Embed(title='**Hypixel commands:**',color=discord.Color.dark_orange())
    embed.add_field(name='**.hypixeluserlookup {username}**', value='Returns all basic stats about a user.', inline=False)
    embed.add_field(name='**.hypixellevel {username}**', value='Returns a users hypixel level.', inline=False)
    embed.add_field(name='**.rankcheck {username}**', value='Returns a users hypixel rank and colour.', inline=False)
    embed.add_field(name='**.karma {username}**', value='Returns a users hypixel Karma.', inline=False)
    embed.add_field(name='**.online {username}**', value='Returns whether a user is online or not.', inline=False)
    await ctx.channel.send(embed=embed)

#latency
@client.command(aliases=['Ping'])
async def ping(ctx):
    embed = discord.Embed(
        description=
        f"Pong! I responded in {float(round(client.latency * 100))} ms. Ain't that impressive!",
        color=discord.Color.magenta())
    await ctx.send(embed=embed)


#hypixel full user lookup
@bot.command(aliases=['HL', 'hl'])
async def hypixeluserlookup(ctx, username):
    mojang_response = requests.get(
        f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if mojang_response.status_code == 200:
        uuid = mojang_response.json()['id']
    else:
        await ctx.channel.send(f'Could not find player {username}')
        return
    # Fetch player data from Hypixel API
    hypixel_response = requests.get(
        f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
    if hypixel_response.status_code == 200 and hypixel_response.json(
    )['success']:
        player_data = hypixel_response.json()['player']
        player_name = player_data['displayname']
        player_online = player_data.get('lastLogin') > player_data.get(
            'lastLogout')  # Online if last login is after last logout
        player_rank = player_data.get(
            'rank',
            player_data.get('newPackageRank',
                            player_data.get('monthlyPackageRank', 'None')))
        player_rank_color = player_data.get(
            'rankPlusColor', 'None')  # Default to 'None' if no color is found
        player_level = (
            player_data['networkExp'] / 10000
        ) if 'networkExp' in player_data else 0  # Hypixel level is derived from network experience
        player_karma = player_data.get('karma', 0)

        embed = discord.Embed(title=f"{player_name}'s basic hypixel stats:",
                              color=discord.Color.dark_orange())
        embed.add_field(name='Display name:', value=player_name, inline=True)
        embed.add_field(name='Online?',
                        value='Yes' if player_online else 'No',
                        inline=True)
        embed.add_field(name='Rank:', value=player_rank, inline=True)
        embed.add_field(name='Rank colour:',
                        value=player_rank_color,
                        inline=True)
        embed.add_field(name='Level:', value=player_level, inline=True)
        embed.add_field(name='Karma:', value=player_karma, inline=True)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested by {ctx.author.name}')

        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send(f'Could not fetch data for player {username}')


#error catch
@hypixeluserlookup.error
async def hypixeluserlookup_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f'The command didnt work\n{error}')
    else:
        await ctx.channel.send(f'The command didnt work\n{error}')


#hypixel user level lookup
@bot.command(aliases=['HLevel', 'hlevel'])
async def hypixellevel(ctx, username):
    mojang_response = requests.get(
        f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if mojang_response.status_code == 200:
        uuid = mojang_response.json()['id']
    else:
        await ctx.channel.send(f'Could not find player {username}')
        return
    # Fetch player data from Hypixel API
    hypixel_response = requests.get(
        f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
    if hypixel_response.status_code == 200 and hypixel_response.json(
    )['success']:
        player_data = hypixel_response.json()['player']
        player_name = player_data['displayname']
        player_level = (
            player_data['networkExp'] / 10000
        ) if 'networkExp' in player_data else 0  # Hypixel level is derived from network experience

        embed = discord.Embed(title=f"{player_name}'s hypixel level:",
                              color=discord.Color.dark_orange())
        embed.add_field(name='Level:', value=player_level, inline=True)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested by {ctx.author.name}')
        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send(f'Could not fetch data for player {username}')


#error catch
@hypixellevel.error
async def hypixellevel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f'The command didnt work\n{error}')
    else:
        await ctx.channel.send(f'The command didnt work\n{error}')


#hypixel check a players rank
@bot.command(aliases=['Hrank', 'rank'])
async def rankcheck(ctx, username):
    mojang_response = requests.get(
        f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if mojang_response.status_code == 200:
        uuid = mojang_response.json()['id']
    else:
        await ctx.channel.send(f'Could not find player {username}')
        return
    # Fetch player data from Hypixel API
    hypixel_response = requests.get(
        f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
    if hypixel_response.status_code == 200 and hypixel_response.json(
    )['success']:
        player_data = hypixel_response.json()['player']
        player_name = player_data['displayname']
        player_rank = player_data.get(
            'rank',
            player_data.get('newPackageRank',
                            player_data.get('monthlyPackageRank', 'None')))
        player_rank_color = player_data.get(
            'rankPlusColor', 'None')  # Default to 'None' if no color is found
        embed = discord.Embed(title="Rank check!",
                              color=discord.Color.dark_orange())
        embed.add_field(name='Display name:', value=player_name, inline=False)
        embed.add_field(name='Rank:', value=player_rank, inline=False)
        embed.add_field(name='Rank colour:',
                        value=player_rank_color,
                        inline=False)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested by {ctx.author.name}')
        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send(f'Could not fetch data for player {username}')


#error catch
@rankcheck.error
async def rankcheck_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f'The command didnt work\n{error}')
    else:
        await ctx.channel.send(f'The command didnt work\n{error}')

#hypixel karma
@bot.command(aliases=['Hk', 'hk'])
async def karma(ctx, username):
    mojang_response = requests.get(
        f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if mojang_response.status_code == 200:
        uuid = mojang_response.json()['id']
    else:
        await ctx.channel.send(f'Could not find player {username}')
        return
    # Fetch player data from Hypixel API
    hypixel_response = requests.get(
        f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
    if hypixel_response.status_code == 200 and hypixel_response.json(
    )['success']:
        player_data = hypixel_response.json()['player']
        player_name = player_data['displayname']
        player_karma = player_data.get('karma', 0)

        embed = discord.Embed(title=f"{player_name}'s Karma:",
                              color=discord.Color.dark_orange())
        embed.add_field(name='Karma:', value=player_karma, inline=True)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested by {ctx.author.name}')

        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send(f'Could not fetch data for player {username}')


#error catch
@karma.error
async def karma_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f'The command didnt work\n{error}')
    else:
        await ctx.channel.send(f'The command didnt work\n{error}')


#hypixel online check
@bot.command(aliases=['Honline', 'online_check'])
async def online(ctx, username):
    mojang_response = requests.get(
        f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if mojang_response.status_code == 200:
        uuid = mojang_response.json()['id']
    else:
        await ctx.channel.send(f'Could not find player {username}')
        return
    # Fetch player data from Hypixel API
    hypixel_response = requests.get(
        f'https://api.hypixel.net/player?key={HYPIXEL_API_KEY}&uuid={uuid}')
    if hypixel_response.status_code == 200 and hypixel_response.json(
    )['success']:
        player_data = hypixel_response.json()['player']
        player_name = player_data['displayname']
        player_online = player_data.get('lastLogin') > player_data.get(
            'lastLogout')  # Online if last login is after last logout

        embed = discord.Embed(title=f"Is {player_name} online?",
                              color=discord.Color.dark_orange())
        embed.add_field(name='||Yes||' if player_online else '||No||',
                        value = '',
                        inline=True)
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Requested by {ctx.author.name}')

        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send(f'Could not fetch data for player {username}')


#error catch
@online.error
async def online_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f'The command didnt work\n{error}')
    else:
        await ctx.channel.send(f'The command didnt work\n{error}')


#ARTISTOTLE BOT
quotes = True
target_user_id = 971628298041970688

@bot.command()
async def quote_toggle(ctx, value: str):
    global quotes
    if value.lower() == 'true':
        quotes = True
        await ctx.send('Quotes are now enabled.')
    elif value.lower() == 'false':
        quotes = False
        await ctx.send('Quotes are now disabled.')
    else:
        await ctx.send('Invalid value. Please use "True" or "False".')

@bot.event
async def on_message(message):
    global quotes
    if quotes:
        print("Passed")
        if message.author.id == target_user_id:
            number = random.randint(1, 100)
            if number < 10:
                quote = random.choice(getQuote)
                await message.channel.send(quote)
    parts = message.content.split(' ')
    for x in parts:
        if x == "Andy" or x == "andy":
            await message.channel.send(
                "We don't say that mans name around here...")
            await message.delete(delay=2)

    else:
        if mention in message.content:
            await message.channel.send(
                f'Hello {message.author.mention}! My prefix is .\nUse .help for a list of commands!'
            )

    # Ensure commands are still processed <-- IMPORTANT else whole bot BREAKS
    await bot.process_commands(message)

@bot.command()
async def quote_status(ctx):
    await ctx.send(quotes)


@bot.command()
async def quote_change_target(ctx, target_value: str):
    global target_user_id
    if target_value.isdigit() and len(target_value) == 18:
        target_user_id = target_value
        await ctx.send(f"Aristotle Bot Target Changed to {target_value}, if broken, run .quote_reset")
    else:
        await ctx.send("Invalid target ID. Please ensure it's a number and 18 digits long.")

@bot.command()
async def quote_reset(ctx):
    global target_user_id
    target_user_id = 971628298041970688
    await ctx.send("Aristotle Bot Reset.")

@bot.command()
async def quote_target(ctx):
    await ctx.send(f"Aristotle is targetting {target_user_id} currently.")

with open('aristotle_quotes.json', 'r') as f:
    getQuote = json.load(f)


#Bot joins VC
@bot.command(pass_context=True)
async def join(ctx):
    if ctx.voice_client:
        await ctx.send("Already in a voice channel.")
    elif (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio('audio.mp3')
        player = voice.play(source)
        await ctx.send(f'Joined {channel}.')
    else:
        await ctx.send(
            "You are not in a voice channel, you must be in a voice channel to run this command!"
        )

#Bot leaves VC
@bot.command(pass_context=True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send(f"I have left the voice channel.")
    else:
        await ctx.send("I am not in a voice channel.")

#Bot joins vc for 5 seconds, plays audio and leaves
@bot.command(pass_context=True)
async def temp_join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio('audio.mp3')
        player = voice.play(source)
        await ctx.send(f'Joined {channel}.')

        # 5 second timer
        await asyncio.sleep(5)

        await voice.disconnect()
        await ctx.send(f'Left {channel}.')
    else:
        await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command!")


# makes sure youtube link is VALID
def is_youtube(url):
    return 'youtube.com' in url or 'youtu.be' in url

# extracts video details from the 'chube
def get_video_info(url):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',
        'extract_flat': False,
        'restrict_filenames': True,
        'force_generic_extractor': False,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            if 'entries' in info_dict:  # Check if it's a playlist
                raise ValueError("Playlist URLs are not supported")
            return {'title': info_dict['title'], 'url': info_dict['url']}
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return None

#plays url with exception of PLAYLISTS
@bot.command()
async def play(ctx, *, url):
    if ctx.author.voice is None:
        return await ctx.send("You need to be in a voice channel to use this command!")

    voice_channel = ctx.author.voice.channel

    if not is_youtube(url):
        return await ctx.send("Invalid YouTube URL!")

    video_info = get_video_info(url)
    if video_info:
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        ctx.voice_client.stop()

        # Define FFmpeg options to handle the audio stream
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        audio_source = discord.FFmpegPCMAudio(video_info['url'], **ffmpeg_options)
        ctx.voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))
        await ctx.send(f"Now playing: {video_info['title']}")
    else:
        await ctx.send("Error fetching YouTube video information or Playlists are not supported.")

#skips current song
@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Skipped the song!")
    else:
        await ctx.send("Not playing any music right now.")

#pauses current song
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the music.")
    else:
        await ctx.send("Not playing any music or already paused.")

#resumes paused song
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")
    else:
        await ctx.send("Not paused or nothing to resume.")


#checks if author is owner
def is_owner(ctx):
    return ctx.author.id == 971628298041970688 or ctx.author.id == 700781757187752036

#murders billy
@bot.command()
@commands.check(is_owner)
async def kill(ctx):
    await ctx.send("i was kil")
    await bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)

@kill.error
async def reboot_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")

#dm specfic
@bot.command(pass_context=True)
@has_permissions(kick_members=True)
async def dm(ctx, user : discord.User, *, message):
        await ctx.message.delete()
        for i in range (1):
            try:
                await user.send(message)
            except:
                await ctx.send(f"Unsuccessfully DMed user, try again later.")
@dm.error
async def dm_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(description='Sorry, you are not allowed to use this command.', color=discord.Color.dark_blue())
            await ctx.send(embed=embed)
        else:
            ctx.send(error)
# Lock Channel
@bot.command(aliases=['Lock'])
@has_permissions(manage_channels=True)
async def lock( ctx, reason=None):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed=discord.Embed(title=f'Channel Locked', description=f'🔒 #{ctx.channel.name} has been locked. Reason: {reason} \nCode ripped off from Jedi :(', color=discord.Color.blue())
        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f'Locked by {ctx.author.name}')
        await ctx.send(embed=embed)
        channel = discord.utils.get(ctx.guild.channels, name="logs")
        embed=discord.Embed(title=f'Channel locked', color=discord.Color.dark_blue())
        embed.add_field(name='Channel name:', value=ctx.channel.mention, inline=False)
        embed.add_field(name='Used by:', value=ctx.author.mention, inline=False)
        await channel.send(embed=embed)
@lock.error
async def lock_error( ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(description='You are not allowed to use this command.', color=discord.Color.red())
            await ctx.channel.send (embed=embed)

    # Unlock Channel
@bot.command(aliases=['Unlock'])
@has_permissions(manage_channels=True)
async def unlock( ctx,):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed=discord.Embed(title=f'Channel Unlocked', description=f'🔓 #{ctx.channel.name} has been unlocked.\nCode ripped off from Jedi :(', color=discord.Color.blue())
        await ctx.channel.send(embed=embed)
@unlock.error
async def unlock_error( ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(description='You are not allowed to use this command.', color=discord.Color.red())
            await ctx.channel.send (embed=embed)

@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked.')


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick people!")
    else:
        embed = discord.Embed(
            description=
            "Sorry, you are not allowed to kick this user.\nOr you haven't inputted this correctly.",
            color=discord.Color.dark_blue())
        await ctx.send(embed=embed)

@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned.')


# Extracts user ID when the user is @mentioned, then assigns to string.
def extract_user_id(mention: str) -> int:
    """
    Extracts the user ID from a mention string.
    
    Parameters:
        mention (str): The mention string in the format <@user_id>
    
    Returns:
        int: The extracted user ID
    """
    match = re.match(r'<@!?(\d+)>', mention)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Invalid mention format")
    

#allows mod to ban user with @mention
@bot.command()
@has_permissions(ban_members=True)
async def unban(ctx, user_mention: str):
    try:
        user_id = extract_user_id(user_mention)
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'User {user.name} has been unbanned.')
    except discord.NotFound:
        await ctx.send(f'User with ID {user_id} not found in the ban list.')
    except discord.HTTPException as e:
        await ctx.send(f'Failed to unban user: {e}')
    except ValueError as e:
        await ctx.send(f'Error: {e}')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to ban people!")

# Muted role
async def mute_user(ctx, member, duration=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    
    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been muted for {duration} seconds.")

    if duration:
        await asyncio.sleep(duration)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted after {duration} seconds.")
#mutes specified member with duration
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int = None):
    if duration == None:
        return await ctx.send("Please specify a duration.")
    if not member:
        return await ctx.send("Please mention a user to mute.")
    if member == ctx.author:
        return await ctx.send("You cannot mute yourself.")
    
    await mute_user(ctx, member, duration)
#unmutes muted user
@bot.command()
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        return await ctx.send("Muted role does not exist.")
    
    await member.remove_roles(muted_role)
    await ctx.send(f"{member.mention} has been unmuted.")

@mute.error
@unmute.error
async def mute_unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user provided.")
    else:
        await ctx.send("An error occurred while trying to mute/unmute the user.")

# Dictionary to store warnings per user !!!
warnings = {}

# allows for user to reset all warnings (should only be performed if bot crashed)
@bot.command()
@commands.has_permissions(administrator=True)
async def reset_warnings(ctx):
    global warnings
    
    # Ask for confirmation
    await ctx.send("Are you sure you want to reset all warnings? Type 'yes' to confirm.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=15)
        
        if confirmation.content.lower() != 'yes':
            await ctx.send("Reset operation canceled. Warnings were not reset.")
            return
        
        warnings = {}
        await ctx.send("All warnings have been reset.")
    
    except TimeoutError:
        await ctx.send("Reset operation timed out. Warnings were not reset.")
    except:
        await ctx.send("An error occurred. Warnings were not reset.")

#allows user to warn users max 3 warns before automatic ban
@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided."):
    if member.id not in warnings:
        warnings[member.id] = 0
    
    warnings[member.id] += 1
    await ctx.send(f'{member.mention} has been warned ({warnings[member.id]}/3). Reason: {reason}')

    if warnings[member.id] >= 3:
        await member.ban(reason=f'Reached 3 warnings ({reason})')
        await ctx.send(f'{member.mention} has been banned for reaching 3 warnings.')
        warnings[member.id] = 0  # resets warnings after banning

#warning errors
@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user provided.")
    else:
        await ctx.send("An error occurred while trying to warn the user.")

#allows users to unwarn users
@bot.command()
@commands.has_permissions(kick_members=True)
async def unwarn(ctx, member: discord.Member):
    if member.id in warnings and warnings[member.id] > 0:
        warnings[member.id] -= 1
        await ctx.send(f'Removed one warning from {member.mention}. Current warnings: {warnings[member.id]}/3')
    else:
        await ctx.send(f'{member.mention} has no warnings to remove.')

#unwarn error catch
@unwarn.error
async def unwarn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user provided.")
    else:
        await ctx.send("An error occurred while trying to unwarn the user.")

#allows users to see current warnings of @'d user
@bot.command()
async def warnings(ctx, member: discord.Member):
    if member.id in warnings:
        await ctx.send(f'{member.mention} has {warnings[member.id]} warnings.')
    else:
        await ctx.send(f'{member.mention} has no warnings.')

#warnings error catch
@warnings.error
async def warnings_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user provided.")

#allows user to clear a specified number of messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("Amount must be a positive number, stop trying to break me :sob:")

    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to also delete the command invocation
    await ctx.send(f"Cleared {len(deleted) - 1} message(s).")  # -1 to exclude the command itself

# Load jokes from JSON file
with open('jokes.json', 'r', encoding='utf-8') as file:
    jokes_data = json.load(file)

# dad jokes command
@bot.command()
async def joke(ctx):
    jokes = jokes_data.get('jokes', [])
    if jokes:
        joke = random.choice(jokes)
        if 'question' in joke and 'answer' in joke:
            await ctx.send(f"**Q:** {joke['question']}\n**A:** {joke['answer']}")
        else:
            await ctx.send("Oops! Something went wrong with the joke format.")
    else:
        await ctx.send("No jokes found in the database.")

#dad joke error catch
@joke.error
async def joke_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("Failed to fetch a joke. Please try again later.")


















client.run(DISCORD_TOKEN)
