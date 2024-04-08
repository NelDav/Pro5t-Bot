import os

import discord
from discord.ext import commands
from discord.commands.context import ApplicationContext
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.voice_states = True
intents.presences = True
intents.members = True

load_dotenv()

token = os.getenv("TOKEN")

client = commands.Bot(intents=intents)

description = '''PRO5T'''

def is_automatic_channel(channel: discord.VoiceChannel):
    try:
        return channel.category.name == "Automatic voice"
    except:
        return False

def get_automatic_member_channel(member: discord.Member) -> discord.VoiceChannel:
    try:
        if is_automatic_channel(member.voice.channel):
            return member.voice.channel
        else:
            return None
    except:
        return None

async def change_member_limit(member: discord.Member, limit: int) -> str:
    channel = get_automatic_member_channel(member)
    if channel is not None:
        await channel.edit(user_limit = limit)
        return None
    else:
        return "You are not in an automatic voice channel!"

async def update_channel(channel: discord.VoiceChannel):
    if channel is not None and is_automatic_channel(channel):
        activity_list = { }
        for member in channel.members:
            if member.activity is not None:
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
            try:
                print("Renamed channel \"{}\" to \"{}\"".format(previous_name, activity_name))
            except:
                pass

async def automatic_category(guild: discord.Guild):
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

    return automation_category

async def empty_channel(guild: discord.Guild):
    automation_category = await automatic_category(guild)

    # Create new channel if there is no empty chanel in automatic category
    empty_channel = None
    for channel in automation_category.channels:
        if len(channel.members) <= 0:
            empty_channel = channel
            break

    if empty_channel is None:
        empty_channel = await guild.create_voice_channel("Lobby", category=automation_category)
        try:
            print("Created new channel")
        except:
            pass

    return empty_channel

async def move_to_automatic_voice(member: discord.Member, guild: discord.Guild):
    automation_category = await automatic_category(guild)
    channel = await empty_channel(guild)
    await member.move_to(channel)
    empty_channel(guild)
    try:
        print("Moved user!")
    except:
        pass

@client.event
async def on_ready():
    try:
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print("------")
    except:
        pass

    for guild in client.guilds:
        await empty_channel(guild)

@client.event
async def on_voice_state_update(member: discord.Member, before, after):

    if after.channel is not None and not is_automatic_channel(after.channel):
        await move_to_automatic_voice(member, client.guilds[0])
        return

    # Delete empty channels
    if before.channel is not None and is_automatic_channel(before.channel) and len(before.channel.members) <= 0:
        name = before.channel.name
        await before.channel.delete()
        try:
            print("Deleted channel \"{}\"".format(name))
        except:
            pass

    if after.channel is not None and len(after.channel.members) > 0:
        await update_channel(after.channel)
        await empty_channel(client.guilds[0])

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if after.voice is not None:
        await update_channel(after.voice.channel)




voice = client.create_group("voice", "Automatic Voice config")

@voice.command()
async def update(ctx: ApplicationContext):
    channel = get_automatic_member_channel(ctx.author)
    if channel is not None:
        update_channel(channel)
        await ctx.respond("Updated channel names.")


@voice.command()
async def limit(ctx: ApplicationContext, number_of_members: str):
    if number_of_members.isnumeric():
        message = await change_member_limit(ctx.author, int(number_of_members))
        if message == None:
            await ctx.respond("The number of users for the channel {} is limited to {} members.".format(ctx.author.voice.channel.name, number_of_members))
        else:
            await ctx.respond(message)
    else:
        await ctx.respond("Please specify the number of members allowed in this channel!")

@voice.command()
async def unlimit(ctx: ApplicationContext):
    message = await change_member_limit(ctx.author, 0)
    if message == None:
        await ctx.respond("The number of users for the channel {} is unlimeted now.".format(ctx.author.voice.channel.name))
    else:
        await ctx.respond(message)

@voice.command()
async def private(ctx: ApplicationContext):
    channel: discord.VoiceChannel = get_automatic_member_channel(ctx.author)
    if channel is not None:
        await channel.set_permissions(ctx.guild.default_role, connect=False)

        for member in channel.members:
            await channel.set_permissions(member, connect=True)
        await ctx.respond("{} is a private channel now.".format(channel.name))
    else:
        await ctx.respond("You are not in an automatic voice channel!")

@voice.command()
async def public(ctx: ApplicationContext):
    channel: discord.VoiceChannel = get_automatic_member_channel(ctx.author)
    if channel is not None:
        await channel.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.respond("{} is a public channel now.".format(channel.name))
    else:
        await ctx.respond("You are not in an automatic voice channel!")

@voice.command()
async def add(ctx: ApplicationContext, member: str):
    channel: discord.VoiceChannel = get_automatic_member_channel(ctx.author)
    if channel is not None:
        if channel.overwrites_for(ctx.guild.default_role).connect is False:
            member = ctx.guild.get_member_named(member)
            if member is not None:
                await channel.set_permissions(member, connect=True)
                await ctx.respond("Added {} to {}.".format(member, channel.name))
            else:
                await ctx.respond("This user is not member of this guild!")
        else:
            await ctx.respond("{} is not a private channel. Use `/voice private` to change!".format(channel.name))
    else:
        await ctx.respond("You are not in an automatic voice channel!")

@voice.command()
async def remove(ctx: ApplicationContext, member: str):
    channel: discord.VoiceChannel = get_automatic_member_channel(ctx.author)
    if channel is not None:
        if channel.overwrites_for(ctx.guild.default_role).connect is False:
            member = ctx.guild.get_member_named(member)
            if member is not None:
                await channel.set_permissions(member, connect=False)
                await ctx.respond("Added {} to {}.".format(member, channel.name))
            else:
                await ctx.respond("This user is not member of this guild!")
        else:
            await ctx.respond("{} is not a private channel. Use `/voice private` to change!".format(channel.name))
    else:
        await ctx.respond("You are not in an automatic voice channel!")

client.run(token)
