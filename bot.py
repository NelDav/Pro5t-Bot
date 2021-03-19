import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.voice_states = True
intents.presences = True
intents.members = True

load_dotenv()

token = os.getenv("TOKEN")

client = commands.Bot(command_prefix='!', intents=intents)

description = '''PRO5T'''

def is_automatic_channel(channel: discord.VoiceChannel):
    try:
        return channel.category.name == "Automatic voice"
    except:
        return False

async def get_automatic_member_channel(member: discord.Member) -> discord.VoiceChannel:
    try:
        if is_automatic_channel(member.voice.channel):
            return member.voice.channel
        else:
            return None
    except:
        return None

async def change_member_limit(member: discord.Member, limit: int) -> str:
    channel = await get_automatic_member_channel(member)
    if channel is not None:
        await channel.edit(user_limit = limit)
        return None
    else:
        return "You are not in an automatic voice channel!"

async def update_channel(channel: discord.VoiceChannel):
    if channel is not None and is_automatic_channel(channel):
        activity_list = { }
        for member in channel.members:
            if not member.activity == None:
                activity_name = member.activity.name

                if activity_name in activity_list:
                    activity_list.update({activity_name : activity_list.get(activity_name) + 1})
                else:
                    activity_list.update({activity_name : 1})

        current_game = None
        if len(channel.members) > 0:
            current_game = ("Allgemein", 0)
        else:
            current_game = ("Lobby", 0)
        for game, value in activity_list.items():
            if value > current_game[1]:
                current_game = (game, value)

        activity_name = current_game[0]
        previous_name = channel.name

        if (not previous_name == activity_name):
            await channel.edit(name=activity_name)
            print("Renamed channel \"{}\" to \"{}\"".format(previous_name, activity_name))

async def create_channel(guild: discord.Guild):
    if guild == None:
        return

    # Find automatic category
    automation_category = None
    for category in guild.categories:
        if category.name == "Automatic voice":
            automation_category = category

    # Create automatic category if it doe not exist
    if automation_category is None:
        automation_category = await guild.create_category("Automatic voice")

    # Create new channel if there is no empty chanel in automatic category
    empty_channel_exists = False
    for channel in automation_category.channels:
        if len(channel.members) <= 0:
            empty_channel_exists = True

    if not empty_channel_exists:
        await guild.create_voice_channel("Lobby", category=automation_category)
        print("Created new channel")

def is_bot_channel(channel: discord.TextChannel) -> bool:
    channel_list = ["commands", "bot-debug"]
    return channel.name in channel_list

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

    for guild in client.guilds:
        await create_channel(guild)

@client.event
async def on_voice_state_update(member: discord.Member, before, after):
    # Delete empty channels
    discord.VoiceChannel.category
    if not before.channel == None and is_automatic_channel(before.channel) and len(before.channel.members) <= 0:
        name = before.channel.name
        await before.channel.delete()
        print("Deleted channel \"{}\"".format(name))

    if after.channel is not None and len(after.channel.members) > 0:
        await update_channel(after.channel)
        await create_channel(client.guilds[0])

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if after.voice is not None:
        await update_channel(after.voice.channel)

@client.command()
async def limit(ctx: commands.Context, number_of_members: str):
    if number_of_members.isnumeric():
        message = await change_member_limit(ctx.author, int(number_of_members))
        if message == None:
            await ctx.send("The number of users for the channel {} is limited to {} members!".format(ctx.author.voice.channel.name, number_of_members))
        else:
            await ctx.send(message)
    else:
        await ctx.send("Please specify the number of members allowed in this channel!")

@client.command()
async def unlimit(ctx: commands.Context):
    message = await change_member_limit(ctx.author, 0)
    if message == None:
        await ctx.send("The number of users for the channel {} is unlimeted now!".format(ctx.author.voice.channel.name))
    else:
        await ctx.send(message)

@client.command()
async def private(ctx: commands.Context):
    if is_bot_channel(ctx.channel):
        channel: discord.VoiceChannel = await get_automatic_member_channel(ctx.author)
        if channel is not None:
            await channel.set_permissions(ctx.guild.default_role, connect=False)
            await channel.set_permissions(ctx.author, connect=True)
            await ctx.send("{} is a private channel now!".format(channel.name))
        else:
            await ctx.send("You are not in an automatic voice channel!")

@client.command()
async def public(ctx: commands.Context):
    if is_bot_channel(ctx.channel):
        channel: discord.VoiceChannel = await get_automatic_member_channel(ctx.author)
        if channel is not None:
            await channel.set_permissions(ctx.guild.default_role, connect=True)
            await ctx.send("{} is a public channel now!".format(channel.name))
        else:
            await ctx.send("You are not in an automatic voice channel!")

@client.command()
async def add(ctx: commands.Context, member: str):
    if is_bot_channel(ctx.channel):
        channel: discord.VoiceChannel = await get_automatic_member_channel(ctx.author)
        if channel is not None:
            if channel.overwrites_for(ctx.guild.default_role).connect is False:
                member = ctx.guild.get_member_named(member)
                if member is not None:
                    await channel.set_permissions(member, connect=True)
                    await ctx.send("Added {} to {}!".format(member, channel.name))
                else:
                    await ctx.send("This user is not member of this guild!")
            else:
                await ctx.send("{} is not a private channel. Use !private to change!".format(channel.name))
        else:
            await ctx.send("You are not in an automatic voice channel!")

@client.command()
async def remove(ctx: commands.Context, member: str):
    if is_bot_channel(ctx.channel):
        channel: discord.VoiceChannel = await get_automatic_member_channel(ctx.author)
        if channel is not None:
            if channel.overwrites_for(ctx.guild.default_role).connect is False:
                member = ctx.guild.get_member_named(member)
                if member is not None:
                    await channel.set_permissions(member, connect=False)
                    await ctx.send("Added {} to {}!".format(member, channel.name))
                else:
                    await ctx.send("This user is not member of this guild!")
            else:
                await ctx.send("{} is not a private channel. Use !private to change!".format(channel.name))
        else:
            await ctx.send("You are not in an automatic voice channel!")

client.run(token)
