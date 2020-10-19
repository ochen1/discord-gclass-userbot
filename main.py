from time import sleep

import discord
import os
from gcapimain import get_info
from json import dumps, loads
from datetime import datetime
from dateutil import tz

if os.getenv("WHITELIST"):
    WHITELISTED_USERS = loads(os.getenv("WHITELIST"))
else:
    WHITELISTED_USERS = list()

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as %s." % client.user)


def try_retrieve_thumbnail(d: dict):
    if 'thumbnailUrl' in d:
        return d['thumbnailUrl']
    else:
        for v in d.values():
            r = try_retrieve_thumbnail(v)
            if r:
                return r


@client.event
async def on_message(message):
    if message.author != client.user and message.author.id not in WHITELISTED_USERS:
        return
    if not message.content.startswith("$gc"):
        return
    try:
        url = message.content.split(' ')[1]
    except IndexError:
        try:
            await message.delete()
        except discord.errors.Forbidden:
            pass
        return
    r = get_info(url)
    print(dumps(r))
    duedate = datetime(
        *r['work']['dueDate'].values(),
        *r['work']['dueTime'].values(),
        tzinfo=tz.tzutc()
    )
    duedate = duedate.astimezone(tz.tzlocal())
    now = datetime.now()
    now = now.astimezone(tz.tzlocal())
    embed = discord.Embed(
        title="%s - %s" % (r['course']['name'], r['work']['title']),
        url=r['work']['alternateLink'],
        description=r['work']['description'],
        color=5315015
    )
    l = None
    for i in r['work']['materials']:
        l = try_retrieve_thumbnail(i)
        if l:
            break
    if l:
        embed.set_thumbnail(url=l)
    embed.set_author(name=r['work']['workType'])
    embed.add_field(name="Materials", value=str(len(r['work']['materials'])), inline=True)
    embed.add_field(name="State", value=r['work']['state'], inline=True)
    embed.add_field(name="Due in", value=str(duedate - now), inline=False)
    embed.add_field(name="Due date", value=str(duedate), inline=False)
    try:
        await message.edit(content="Here is a Google Classroom link:", embed=embed)
    except discord.errors.Forbidden:
        try:
            await message.delete()
        except discord.errors.Forbidden:
            pass
        await message.channel.send("Here is a Google Classroom link:", embed=embed)


client.run(os.getenv('TOKEN'), bot=False)
