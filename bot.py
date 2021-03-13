import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from asyncio import sleep

from discord import Member

intents = discord.Intents.default()
intents.voice_states = True
intents.presences = True
intents.members = True

load_dotenv()

token = os.getenv("TOKEN")

client = discord.Client(intents=intents)

commander = commands.Bot(command_prefix='!')

description = '''PRO5T'''

async def update_channel(channel: discord.VoiceChannel):
    if channel == None:
        return

    activity_list = { }
    for member in channel.members:
        activity_name = "Allgemein"
        if not member.activity == None:
            activity_name = member.activity.name

        if activity_name in activity_list:
            activity_list.update({activity_name : activity_list.get(member.activity) + 1})
        else:
            activity_list.update({activity_name : 1})
    
    current_game = ("Empty", 0)
    for game, value in activity_list.items():
        if value > current_game[1]:
            current_game = (game, value)
    
    activity_name = current_game[0]

    await channel.edit(name=activity_name)

async def create_channel(guild: discord.Guild):
    if guild == None:
        return

    automation_category = None
    for category in guild.categories:
        if category.name == "Automatic voice":
            automation_category = category

    if automation_category == None:
        automation_category = await guild.create_category("Automatic voice")

    empty_channel_exists = False
    for channel in automation_category.channels:
        if len(channel.members) <= 0:
            empty_channel_exists = True

    if not empty_channel_exists:
        await guild.create_voice_channel("Empty", category=automation_category)


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
    if not before.channel == None and before.channel.category.name == ("Automatic voice") and len(before.channel.members) <= 0:
        await before.channel.delete()

    if not after.channel == None and after.channel.category.name == ("Automatic voice") and len(after.channel.members) > 0:
        await update_channel(after.channel)
        await create_channel(client.guilds[0])

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await update_channel(after.voice.channel)

@commander.command()
async def update(ctx):
    await update_channel(ctx.author.voice.channel)
    await ctx.send("Sucessfully updated!")

client.run(token)