from pickle import TRUE
import discord
import random
import utils
import datetime
import os
import ast

from dateutil import tz
from discord.ext import tasks
from discord.ext.commands import Bot,AutoShardedBot

from classes.dis_events import DiscordEvents
from classes.subscribe import Subscribe
from classes.subscribemenu import SubscribeView
from classes.config import Config
from classes.reputation import Reputation
from dataclasses import dataclass



# #######################################
# The OMFClient class
# #######################################


class OMFBot(AutoShardedBot):


    # each guild has the following elements:
    # - a list of scheduled Events (EventsList)
    # - a list of Messages that will be sent at idle times
    # - a timer indicating the number of scheduler runs to
    #   wait before a new idle message is sent

    @dataclass
    class GuildData:
        EventsList = {}
        idle_messages=[]
        channel_idle_timer=0
        ReputationFilter:Reputation = None

    # the guildDataList contains one GuildData class per item.
    # the key is the guild ID

    guildDataList={}

    # configData is the generic config object that reads / writes
    # the config data to disk

    configData:Config

    # EventsClass is the interface to the restful api
    # that allows us to create scheduled events

    EventsClass : DiscordEvents

    # #######################################
    # init constructor
    # #######################################

    def __init__(self) -> None:
        # Try to set all intents
        intents = discord.Intents.all()
        super().__init__(command_prefix="!",intents=intents)
        self.prefix="!"
        self.configData=Config('config.json')


        # The subscribe command will add/remove the notification roles 
        # based on the scheduled events
        @self.tree.command(name="subscribe", description="(un)subscribe to Events)")
        async def subscribe(interaction: discord.Interaction):

            #x:      Subscribe
            x:      SubscribeView
            member: discord.Member
           
            guildNode=self.configData.readGuild(interaction.guild.id)
            member = interaction.user
            #x=Subscribe(autoEvents=guildNode["AUTO_EVENTS"],member=member)
            #await interaction.response.send_modal(x)
            x=SubscribeView(autoEvents=guildNode["AUTO_EVENTS"],member=member)
            print(x)
            await interaction.response.send_message("Chose",view=x ,ephemeral=True)

        # The setup command will ask for the guild parameters and
        # read them in
        @self.tree.command(name="setup", description="Define parameters for the bot")
        async def setup(
            interaction: discord.Interaction, 
            template_channel:discord.TextChannel,
            idle_channel:discord.TextChannel,
            idle_sleepcycles:int,
            avoid_spam:int):

            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f'only an Administrator can do that', ephemeral=True)
            else:
                try:
                    jData={
                            "IDLE_MESSAGE_CHANNEL_ID" : idle_channel.id,
                            "CONFIG_CHANNEL_ID": template_channel.id,
                            "CHANNEL_IDLE_INTERVAL" : idle_sleepcycles,
                            "AVOID_SPAM" : avoid_spam,
                            "AUTO_EVENTS": []
                          }
                    self.configData.writeGuild(interaction.guild.id,jData)
                    await interaction.response.send_message(f'All updated\nThank you for using my services!\nyou might need to run /update', ephemeral=True)
                except Exception as e:
                    print(f"ERROR in setup command: {e}")
                    await interaction.response.send_message(f'Ooops, there was a glitch!', ephemeral=True)

        # The update command will read the guild configs from the 
        # message templates channel
        @self.tree.command(name="update", description="read in the message templates and update the cache")
        async def update(interaction: discord.Interaction):
            
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f'only an Administrator can do that', ephemeral=True)
            else:
                try:
                    await self.readMessageTemplates(interaction.guild)
                    #self.configData.writeGuild(interaction.guild.id,jData)

                    numMessages=len(self.guildDataList[f'{interaction.guild.id}'].idle_messages)
                    guildNode=self.configData.readGuild(interaction.guild.id)
                    eventNodes=guildNode["AUTO_EVENTS"]
                    numEvents=len(eventNodes)
                    numRoles=len(self.guildDataList[f'{interaction.guild.id}'].ReputationFilter.reputationRoles)

                    await interaction.response.send_message(f'{numRoles} reputation roles, {numEvents} Events and {numMessages} Message templates\nThank you for using my services!', ephemeral=True)
                except Exception as e:
                    print(f"ERROR in update command: {e}")
                    await interaction.response.send_message(f'Ooops, there was a glitch!', ephemeral=True)

        @self.tree.command(name="say_ralf", description="admin function")
        async def say_ralf(
            interaction: discord.Interaction, 
            which_channel:discord.TextChannel,
            message:str):
            
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(f'only an Administrator can do that', ephemeral=True)
            else:
                try:
                    await which_channel.send(message)
                    await interaction.response.send_message('message sent', ephemeral=True)
                except Exception as e:
                    print(f"ERROR in say_ralf: {e}")
                    await interaction.response.send_message(f'Ooops, there was a glitch!', ephemeral=True)

        @self.tree.command(name="reputation", description="shows your reputation")
        async def update(interaction: discord.Interaction):
            
                try:

                    userReputation=self.guildDataList[f'{interaction.guild.id}'].ReputationFilter.getReputation(interaction.user,True)
                    await interaction.response.send_message(userReputation, ephemeral=True)
                except Exception as e:
                    print(f"ERROR in update command: {e}")
                    await interaction.response.send_message(f'Ooops, there was a glitch!', ephemeral=True)

    # ################################
    # the bot run command just starts 
    # the bot with the token from
    # the json config file
    # ################################

    def  run(self,*args, **kwargs):
        super().run(token=self.configData.getToken())

    # #########################
    # setup_hook waits for the
    # command tree to sync
    # and loads the cogs
    # #########################

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        await self.tree.sync()
        # load all cogs
        try:
            for file in os.listdir("cogs"):
                if file.endswith(".py"):
                    name = file[:-3]
                    await self.load_extension(f"cogs.{name}")
        except Exception as e:
            print(f"ERROR in setup_hook: {e}")


    # ######################################################
    # send_random_message is called when the server is idle
    # and posts a random message to the server
    # ######################################################

    async def send_random_message(self,guildID):
        guildNode=self.configData.readGuild(guildID)
        print("Sending random message")
        idle_channel_id=guildNode["IDLE_MESSAGE_CHANNEL_ID"]
        idle_channel=self.get_channel(idle_channel_id)
        gdn:self.GuildData
        gdn=self.guildDataList[f'{guildID}']
        idle_messages=gdn.idle_messages

        # if the author of the previously last sent message and 
        # the new message is ourselves, then delete the 
        # previous message
        try:
            lastSentMessage = await idle_channel.fetch_message(
                idle_channel.last_message_id)
            if  (int(f'{guildNode["AVOID_SPAM"]}') == 1) and (lastSentMessage is not None):
                if (lastSentMessage.author == self.user):
                    await lastSentMessage.delete()
        except Exception as e:
            print(f"delete lastmessage error: {e}")

        try:
            await idle_channel.send(f'{random.choice(idle_messages)}')
        except Exception as e:
            print(f"send random message error: {e}")
        
    # ######################################################
    # readMessageTemplates reads all messages from
    # the guildID/"config"/"CONFIG_CHANNEL_ID"] node
    # of the configdata and stores it in the idleMessages dict
    # in an array under the guild ID key
    # ######################################################

    async def readMessageTemplates(self,theGuild:discord.Guild):

        # we init the guild data with a new GuildData object
        self.guildDataList[f'{theGuild.id}'] = self.GuildData(None)

        guildNode=self.configData.readGuild(theGuild.id)
        if guildNode is None:
            print (f"Guild {theGuild.id} has no setup")
            return
        
        # if we have data for that guild then we try to read in the template messages from
        # the predefined template channel

        theTemplateChannel:discord.TextChannel
        theTemplateChannel=theGuild.get_channel(int(guildNode["CONFIG_CHANNEL_ID"]))
        message:discord.Message
        messages = theTemplateChannel.history(limit=50)
        self.guildDataList[f'{theGuild.id}'].idle_messages=[]
        eventNodes=[]

        # configuration for events and reputation are json objects
        # everything else is considered to be an idle message that
        # is randomly being sent into the configured channel

        async for message in messages: 
            messageContent:str
            messageContent=message.content
            try:

                # if the message is a dictionary then it is either an event
                # or a list of reputation roles

                someDict=ast.literal_eval(messageContent)
                if isinstance(someDict, dict):
                    try:
                        if (someDict["REPUTATION"] is not None):
                            allKeys=someDict["REPUTATION"]

                            # the "MUTE" key contains the role that is assigned to a user
                            # who sent too many messages and ignored the warnings

                            self.guildDataList[f'{theGuild.id}'].ReputationFilter = Reputation(theGuild,40,allKeys["MUTE"])
                            for rep in allKeys:
                                if (rep != "MUTE" ):

                                    # other roles increaese the reputation
                                    print("Role ", str(rep)," adds Reputation ",allKeys[rep])
                                    self.guildDataList[f'{theGuild.id}'].ReputationFilter.addReputationRole(int(rep),int(allKeys[rep]))
                    except Exception as ee:
                        eventNodes.append(someDict)
            except Exception as e:
                self.guildDataList[f'{theGuild.id}'].idle_messages.append(message.content)

        # the "AUTO_EVENTS" node contains all the planned events
                
        guildNode["AUTO_EVENTS"]=eventNodes
        self.configData.writeGuild(theGuild.id,guildNode)

        numMessages=len(self.guildDataList[f'{theGuild.id}'].idle_messages)
        numEvents=len(eventNodes)
        print(f'{numEvents} Events and {numMessages} Message templates')


    # ######################################################
    # on_ready is called once the client is initialized
    # it then reads in the files in the config.IDLE_MESSAGE_DIR
    # directory and starts the schedulers
    # ######################################################

    async def on_ready(self):
        print('Logged on as', self.user)

        self.EventsClass = DiscordEvents(
            discord_token=self.configData.getToken(),
            client_id=self.configData.getClientID(),
            bot_permissions=8,
            api_version=10)

        # read in the random message files
        # the idle_messages array holds one element per message
        # every message is read in as a whole into one element of the array

        for theGuild in self.guilds:
            await self.readMessageTemplates(theGuild)            

        # start the schedulers

        self.task_scheduler.start()
        self.daily_tasks.start()



    # ######################################################
    # create_events will create the Sunday Funday events
    # for the next sunday
    # ######################################################

    async def create_events (self,theGuild):

        print("Create Events")

        guildNode=self.configData.readGuild(theGuild.id)
        eventNodes=guildNode["AUTO_EVENTS"]

        for theEvent in eventNodes:

            # calculate the date of the future event
            theDate:datetime.datetime = utils.onDay(datetime.date.today(),theEvent['day_of_week'])
            # we need the offset from local time to UTC for the date of the event,
            # not the date when we create the event. The event is on a Sunday and might be the
            # first daylight saving day
            utcOffset=tz.tzlocal().utcoffset(datetime.datetime.strptime(f"{theDate}","%Y-%m-%d"))
            # the times are stored in local time in the dictionary but will
            # be UTC in the discord API
            utcStartTime=format(datetime.datetime.strptime(theEvent['start_time'],"%H:%M:%S")-utcOffset,"%H:%M:%S")
            utcEndTime=format(datetime.datetime.strptime(theEvent['end_time'],"%H:%M:%S")-utcOffset,"%H:%M:%S")
            # Now we just add the date portion and the time portion
            # of course this will not work for events where the UTCOffset is bigger 
            # than the start time - for Germany this is OK as long as the start time is
            # after 2 AM
            strStart=theDate.strftime(f"%Y-%m-%dT{utcStartTime}")
            strEnd=theDate.strftime(f"%Y-%m-%dT{utcEndTime}")

            await self.EventsClass.create_guild_event(
                event_name=theEvent['title'],
                event_description=theEvent['description'],
                event_start_time=f"{strStart}",
                event_end_time=f"{strEnd}",
                event_metadata={},
                event_privacy_level=2,
                channel_id=theEvent['channel'],
                guild_id=theGuild.id)
            # once we have created the event, we let everyone know 
            channel = theGuild.get_channel(guildNode["IDLE_MESSAGE_CHANNEL_ID"])
            await channel.send(f'Hi - I have created the scheduled Event {theEvent["title"]}')


    # ######################################################
    # get_event_list gives a list of scheduled events
    # ######################################################

    async def get_events_list (self,theGuild: discord.Guild):

        eventList = await self.EventsClass.list_guild_events(theGuild.id)
        self.guildDataList[f'{theGuild.id}'].EventsList = eventList
        return eventList

    # ######################################################
    # on_message scans for message contents and takes 
    # corresponding actions.
    # User sends ping - bot replies with pong
    # User asks a question - bot checks if question has been 
    # answered
    # ######################################################

    async def on_message(self, message  : discord.Message ):

        # ignore ephemeral messages
        if message.flags.ephemeral:
            return

        print("{} has just sent {}".format(message.author, message.content))

        # don't respond to ourselves
        if message.author == self.user:
            return

        reputationFilter=self.guildDataList[f'{message.guild.id}'].ReputationFilter
        if not (reputationFilter is None):
            theScore=await reputationFilter.checkMessage(message)
            # user is throtteled or muted
            if (theScore<=0):
                await message.reply("Hold your horses - **you are sending too many messages**\nHave you sent a lot of links?\nIf you continue to send then **you will be muted**\n**contact an admin** in order to have you added to a trusted role\n")
            if (theScore<=-1):
                await message.reply("**You have sent too many messages**\nHave you sent a lot of links?\n**you are now muted**\nAdmins have been alerted and will examine the situation\nIf this was a false alert then you will be unblocked soon")

        # reset the idle timer if a message has been sent or received
        self.guildDataList[f'{message.guild.id}'].channel_idle_timer=0
        await self.process_commands(message)


    # ######################################################
    # on_typing detects if a user types. 
    # We might use this one day to have users agree to policies etc.
    # before they are allowed to speak
    # or we might launch the Support() Modal if a user starts
    # to type in the support channel
    # ######################################################

    async def on_typing(self, channel, user, _):
        # we do not want the bot to reply to itself
        if user.id == self.user.id:
            return
        print(f"{user} is typing in {channel}")
        self.channel_idle_timer = 0
        #await channel.trigger_typing()

    # ######################################################
    # daily_tasks runs once a day and checks the following:
    # - does an event need to be created ?
    # ######################################################

    @tasks.loop(hours=24)
    async def daily_tasks(self):
        print("DAILY TASKS")

        # Every Monday (weekday 0) we want to create the 
        # scheduled events for the next Sunday

        if datetime.date.today().weekday() == 0:
            print("create events")
            for theGuild in self.guilds:
                try:
                    await self.create_events(theGuild=theGuild)
                except Exception as e:
                    print(f"Daily Task create Events failed: {e}")


    # ######################################################
    # task_scheduler is the main supervisor task
    # it runs every 10 minutes and checks the following:
    # - has a question been asked that has not been answered ?
    # - do reminders need to be sent out ?
    # - does a random message need to be sent out ?
    # ######################################################


    @tasks.loop(minutes=10)
    async def task_scheduler(self):

        print("SCHEDULE")

        for theGuild in self.guilds:
            guildNode=self.configData.readGuild(theGuild.id)
            if guildNode is None:
                print (f"Guild {theGuild.id} has no setup")
                continue
            gdn:self.GuildData
            gdn=self.guildDataList[f'{theGuild.id}']
            gdn.channel_idle_timer += 1

            # #####################################
            # see if we need to send a random message
            # if the counter is greater than CHANNEL_IDLE_INTERVAL
            # then send a random message into the idle_channel
            # #####################################

            try:
                if gdn.channel_idle_timer >= guildNode["CHANNEL_IDLE_INTERVAL"]:
                    gdn.channel_idle_timer = 0
                    await self.send_random_message(guildID=theGuild.id)
            except Exception as e:
                print(f"Scheduler random_message failed: {e}")

            # see if we need to send out notifications for events
            # The Event details are stored in config.
            eventList=None
            
            for theEvent in guildNode["AUTO_EVENTS"]:
                # first let's convert the String dates to datetime:
                theDate=utils.onDay(datetime.date.today(),theEvent['day_of_week'])
                startTime=theEvent['start_time']
                eventScheduledTimeDate=datetime.datetime.fromisoformat (theDate.strftime(f"%Y-%m-%dT{startTime}"))
                # now let's figure out the time deltas:
                timeUntilEvent=eventScheduledTimeDate - datetime.datetime.today()
                earliestPing=eventScheduledTimeDate - datetime.timedelta(minutes=theEvent["notify_minutes"]) - datetime.timedelta(minutes=10)
                latestPing=eventScheduledTimeDate - datetime.timedelta(minutes=theEvent["notify_minutes"])  
                #print("found scheduled event")
                #print(f"The event is on {theDate} at {startTime} - that is in {timeUntilEvent}")
                #print (f"we ping between {earliestPing} and {latestPing}")
                # If we are in the interval then let's initiate the reminder
                if (earliestPing < datetime.datetime.today() <= latestPing):
                    # let's first check if the event is still on
                    # it may have been deleted or modified on the server
                    # we don't want to alert for non-existing events
                    # we'll just use the title to compare for the time being.
                    print("Let me check if the event is still on")
                    try:
                        if eventList == None:
                            eventList = await self.get_events_list(theGuild=theGuild)
                        for theScheduledEvent in eventList:
                            if theScheduledEvent["name"] == theEvent["title"]:
                                channel = self.get_channel(guildNode["IDLE_MESSAGE_CHANNEL_ID"])
                                theMessageText=f'Hi <@&{theEvent["subscription_role_num"]}>, the event *** {theEvent["title"]} *** will start in roughly {theEvent["notify_minutes"]} minutes in the <#{theEvent["channel"]}> channel. {theEvent["description"]}'
                                await channel.send(f"{theMessageText}")
                    except Exception as e:
                        print(f"Scheduler event_reminder failed: {e}")
