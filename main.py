#Discord.py Bot Template, by Zennara#8377
#This template is a compilation of code to make it easier to design your own Discord.py Bot
#I made this for my own use, but don't care who uses it, but please credit me if someone asks :)

#imports
import discord #api
import os #for virtual environment secrets on replit
import keep_alive #this keeps our bot alive from the keep_alive.py file
import asyncio #not needed unless creating loop tasks etc (you'll run into it)
import json #to write db to a json file
import requests #to check discord api for limits/bans
from replit import db #database storage
import time
from datetime import datetime

#api limit checker
#rate limits occur when you access the api too much. You can view Discord.py's api below. There it will tell you whether an action will access the api.
#https://discordpy.readthedocs.io/en/stable/api.html
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"You are being Rate Limited : {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all() #declare what Intents you use, these will be checked in the Discord dev portal
client = discord.Client(intents=intents)

#error message
async def error(message, code):
  await message.channel.send("```\n"+code+"\n```")

@client.event
async def on_ready():
  print("\n/sbin/ Ready.\n")
  global startDate
  startDate = datetime.now()
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="in the shell"))

@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  #convert the message to all lowercase
  messagecontent = message.content.lower()

  #this will clear the database if something is broken, WARNING: will delete all entries
  if messagecontent == "$ clear":
    #my database entries are seperates by server id for each key. this works MOST of the time unless you have a large amount of data
    db[str(message.guild.id)] = {"prefix": "$", "role_reactions":[]}

  #get prefix
  prefix = db[str(message.guild.id)]["prefix"]

  #this is to dump your databse into database.json. Change this to FALSE to stop this.
  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  #get uptime
  global startDate
  uptime = datetime.now() - startDate
      
  #ping command
  if messagecontent == prefix+" ping":
    await message.channel.send("```\n/sbin/ has been online for " + str(uptime) + "\n```")

  #uname command
  if messagecontent == prefix+" uname":
    await message.channel.send("```\n/sbin/ Bot\nAuthor:       Zennara#8377\nCreated:      1/7/2021\nPublic:       False\nDescription:  A custom bot for this server. This can't be found anywhere else.\n```")

  #neofeatch
  if messagecontent == prefix+" neofetch":
    await message.channel.send("""```
         , - ~ ~ ~ - ,             /sbin/ Discord Bot
     , '               ' ,       . ------------------
   ,      .                ,     . Host: repl.it
  ,     /#|#\               ,    . Uptime: """+str(uptime)+"""
 ,      # |                  ,   . Version: 1.0.0
 ,      \#|#\                ,   . Library: Discord.py 1.7.3
 ,        | #                ,   . Packages: 9
  ,     \#|#/  ______       ,    . Theme: Linux Terminal
   ,      '                ,     . Prefix: $
     ,                   ,       . Author: Zennara#8377
       ' - , _ _ _ , - '         . Status: Custom, Private
    ```""")

  #echo command
  if messagecontent.startswith(prefix+" echo"):
    if len(messagecontent.split(" ",2)) >= 3:
      await message.channel.send("```\n"+message.content.split(" ",2)[2]+"\n```")

  #ls command
  if messagecontent.startswith(prefix+" ls"):
    if messagecontent == prefix+" ls roles":
      text = "```\nno role reactions found\n```"
      if db[str(message.guild.id)]["role_reactions"]:
        text = "```\n"
        for role in db[str(message.guild.id)]["role_reactions"]:
          text += "#"+str(client.get_channel(int(role[0])))+"   "+str(role[1])+"   "+str(message.guild.get_role(int(role[2])))+"   "+str(role[3]) + "\n"
      await message.channel.send(text+"\n```")
      
  #cp
  if messagecontent.startswith(prefix+" cp"):
    splits = messagecontent.split()
    if len(splits) == 5:
      channelID = splits[2][-37:-19]
      messageID = splits[2][-18:]
      roleID = splits[3].replace("<","").replace(">","").replace("&","").replace("@","")
      emoji = splits[4].replace(">","")[-18:]
      if channelID.isnumeric() and messageID.isnumeric():
        if client.get_channel(int(channelID)):
          channel = client.get_channel(int(channelID))
          if await channel.fetch_message(int(messageID)):
            msg = await channel.fetch_message(int(messageID))
            if roleID.isnumeric():
              if message.guild.get_role(int(roleID)):
                try:
                  await msg.add_reaction(emoji)
                except:
                  await error(message, "cp: "+roleID+": invalid emoji")
                else:
                  db[str(message.guild.id)]["role_reactions"].append([channelID,messageID,roleID,emoji])
                  await message.channel.send("```\nrole reaction added\n```")
              else:
                await error(message, "cp: "+roleID+": invalid role")
            else:
              await error(message, "cp: "+roleID+": role id not numeric")
          else:
            await error(message, "cp: "+splits[2]+": invalid message")
        else:
          await error(message, "cp: "+splits[2]+": invalid channel")
      else:
        await error(message, "cp: "+splits[2]+": channel or message not numeric")
    else:
      await error(message, "cp: not enough arguments passed")
  
  
@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "$"} #for database support


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Add a secret environment variable named TOKEN in replit (lock icon on left sidebar)
client.run(os.environ.get("TOKEN"))