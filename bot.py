import discord
from discord import ButtonStyle, app_commands
from numpy import real
import random
import asyncio
from glob import glob
import numpy as np
import config
from asyncio import TimeoutError
from secret import BOT_TOKEN, GUILD_ID

# #######################################
# The OMFClient class
# #######################################


class OMFClient(discord.Client):

    channel_idle_timer: int
    asked_question = False

    # #######################################
    # init constructor
    # #######################################

    def __init__(self) -> None:

        print('Init')
        
        # Try to set all intents

        intents = discord.Intents.all()
        super().__init__(intents=intents)

        # We need a `discord.app_commands.CommandTree` instance
        # to register application commands (slash commands in this case)

        self.channel_idle_timer = 0
        self.idle_channel =  self.get_channel(config.IDLE_MESSAGE_CHANNEL_ID)


    # ######################################################
    # send_random_message is called when the server is idle
    # and posts a random message to the server
    # ######################################################

    async def send_random_message(self):
        print("Sending random message")
        if self.idle_channel == None:
            self.idle_channel = self.get_channel(config.IDLE_MESSAGE_CHANNEL_ID)
        await self.idle_channel.send(f"{random.choice(self.idle_messages)}")

    # ######################################################
    # on_ready is called once the client is initialized
    # it then reads in the files in the config.IDLE_MESSAGE_DIR
    # directory and posts them randomly every
    # config.CHANNEL_IDLE_INTERVAL seconds into the
    # config.IDLE_MESSAGE_CHANNEL_ID channel
    # ######################################################

    async def on_ready(self):
        print('Logged on as', self.user)

        # read in the random message files
        # the idle_messages array holds one element per message
        # every file is read in as a whole into one element of the array

        self.idle_messages = []

        for filename in glob(config.IDLE_MESSAGE_DIR + '/*.txt'):
            print ("read {}",filename)
            with open(filename) as f:
                self.idle_messages.append(f.read())

        self.idle_messages = np.array(self.idle_messages)    

        # every minute increase the idle counter
        # if the counter is greater than CHANNEL_IDLE_INTERVAL
        # then send a random message into the idle_channel
        # the sleep is non-blocking, i.e. the bot will work normally
        # despite the endless loop.

        while True:
            await asyncio.sleep(1)
            self.channel_idle_timer = self.channel_idle_timer + 1
            if self.channel_idle_timer >= config.CHANNEL_IDLE_INTERVAL:
                self.channel_idle_timer = 0
                await self.send_random_message()

    # ######################################################
    # handle_ping is called when a user sends ping
    # it just replies with pong
    # ######################################################

    async def handle_ping (self,message : discord.Message):
        await message.channel.send('pong', reference=message)

    # ######################################################
    # on_message scans for message contents and takes 
    # corresponding actions.
    # User sends ping - bot replies with pong
    # User asks a question - bot checks if question has been 
    # answered
    # ######################################################

    async def on_message(self, message  : discord.Message ):
        print("{} has just sent {}".format(message.author, message.content))

        # don't respond to ourselves
        if message.author == self.user:
            return
        # reset the idle timer if a message has been sent or received
        self.channel_idle_timer = 0

        # reply to ping
        if message.content == 'ping':
           await self.handle_ping(message)
          

    # ######################################################
    # on_typing detects if a user types. 
    # We might use this one day to have users agree to policies etc.
    # before they are allowed to speak
    # ######################################################


    async def on_typing(self, channel, user, _):
        # we do not want the bot to reply to itself
        if user.id == self.user.id:
            return
        print(f"{user} is typing in {channel}")
        self.channel_idle_timer = 0
        #await channel.trigger_typing()


    
