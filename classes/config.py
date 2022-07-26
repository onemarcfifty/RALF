import json

# very rudimentary implementation of a
# generic config class using a json File
# this is OK for few clients.
# for many (>100) clients we should consider file locking
# for very many (>10000) clients we should use a database

class Config():

    configFileName:str
    cfg:json

    def __init__(self,filename:str) -> None:

        self.configFileName = filename
        self.readConfig()

    def readConfig(self) -> json:
        try:
            f = open(self.configFileName)
            self.cfg = json.load(f)
            f.close()
        except Exception as e:
            print(f"Error reading Config Data: {e}")

    def writeConfig(self):
        try:
            with open(self.configFileName, 'w', encoding='utf-8') as f:
                json.dump(self.cfg, f, ensure_ascii=False, indent=5)
                f.close()
        except Exception as e:
            print(f"Error writing Config Data: {e}")


    def getNode(self,nodeID:str):
        if nodeID in self.cfg:
            return self.cfg[nodeID]
        else:
            return None

    def getToken(self):
        secretNode=self.getNode("secret")
        return secretNode.get('BOT_TOKEN')

    def getClientID(self):
        secretNode=self.getNode("secret")
        return secretNode.get('CLIENT_ID')

    def readGuild(self,guildID) -> json:
        guildNode=self.getNode("guilds")
        return guildNode.get(f"{guildID}")

    def writeGuild(self,guildID,nodeData):
        guildNode=self.getNode("guilds")
        guildNode[f"{guildID}"]=nodeData
        self.writeConfig()



# the config.json contains the following main nodes:

# #######################
# "secret"
# #######################

# the secret key contains the following items:

# the BOT_TOKEN is the Oauth2 token for your bot
# example: "BOT_TOKEN" : "DFHEZRERZQRJTSUPERSECRETTTOKENUTZZH"

# #######################
# "guilds"
# #######################

# the guilds node contains all guild specific items, such as channel IDs
# that node will be created if the /setup command is used

# "CONFIG_CHANNEL_ID" is the ID of the channel where the
# idle message templates are located

# "IDLE_MESSAGE_CHANNEL_ID" is the ID of the channel where the
# bot posts a message about the new "ticket"

# QUESTION_SLEEPING_TIME (number)
# # Variable that indicates when the bot answers after a question has been asked
# (in scheduler cycles)
