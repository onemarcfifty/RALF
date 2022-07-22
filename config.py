import json

# Config data is stored in config.json
# see the config.json.example file and below comments
# readConfig() reads the file

cfg = None
AUTO_EVENTS  = []
SECRETS = {}
CONFIG = {}

def readConfig():
    try:
        f = open('config.json')
        global cfg
        cfg = json.load(f)
        #configData = json.loads(data)
        f.close()
        global AUTO_EVENTS
        AUTO_EVENTS = cfg["AUTO_EVENTS"]
        global CONFIG
        CONFIG = cfg["config"]
        global SECRETS
        SECRETS = cfg["secret"]
    except Exception as e:
        print(f"Error reading Config Data: {e}")

# the config.json contains the following main nodes:

# #######################
# "secret"
# #######################

# the secret key contains the following items:

# the BOT_TOKEN is the Oauth2 token for your bot
# example: "BOT_TOKEN" : "DFHEZRERZQRJTSUPERSECRETTTOKENUTZZH"

# The GUILD_ID is the ID of your Server - in the discord client,
# right click on your server and select " copy ID" to get it
# example: "GUILD_ID" : "0236540000563456"

# The client ID can be copied from your App settings page and is needed
# to authenticate with the Discord Restful API for Event creation
# example "CLIENT_ID" : "9990236500564536"

# #######################
# "config"
# #######################

# the config node contains all generic config items, such as channel IDs
# and scheduler variables

# CHANNEL_IDLE_INTERVAL (number)
# the number of scheduler cycles that the channel needs to be idle 
# before the bot posts a generic "did you know" 
# message

# IDLE_MESSAGE_DIR (path without trailing slash)
# the name of the directory where the text files are
# located which contain the messages
# which the bot will randomly send
#  (1 file = 1 message)

# IDLE_MESSAGE_CHANNEL_ID
# the channel where the bot will post messages to

# QUESTION_SLEEPING_TIME (number)
# # Variable that indicates when the bot answers after a question has been asked
# (in scheduler cycles)

# #######################
# "AUTO_EVENTS"
# #######################

# The Auto Events.
# this is used in three contexts:
# 1. Automatic creation of the event
# 2. Automatic reminder of subscribed users
# 3. in the /subscribe command
# this needs to be an array of dict
