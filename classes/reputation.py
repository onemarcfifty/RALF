import string
import discord
from dataclasses import dataclass
import datetime


# The impact of a role on reputation
@dataclass
class ReputationRole:
    roleid:int
    score:int

# what we retain from a message
# the Content, if it contains a link and the user who sent the message
@dataclass
class MessageData:
    Messagecontent:string
    user:discord.Member

# ##########################################################
# Reputation class
# the class that manages the user's reputations.
# Each user has an initial reputation
# that is influenced by the time he/she is on the server 
# and roles that are assigned to the user 
# (e.g. VIPs can have a high reputation, new users a very 
# low one)
# each message that a user sends gives a penalty on the reputation
# each link gives a higher penalty
# only the last x messages are evaluated, i.e. after a certain
# amount of messages the reputation goes back to the initial 
# stage (unless you had been muted in between, then you need
# an admin to unblock)
# ##########################################################


class Reputation:

    # the initialReputation you have
    initialReputation=10

    # the penalty in reputation for posting a link
    linkPenalty=-5

    # the penalty in reputation for posting a message
    messagePenalty=-1

    # the reputation threshold that will throttle a user
    throttleThreshold=5

    # the reputation threshold that will mute a user
    muteThreshold=0

    # the number of messages that one can send in the buffer timeframe that will trigger checks
    triggerCheckThreshold=1

    # other objects that we may want to refer to

    # the bot that called us
    theGuild:discord.Guild

    # the number of last seen messages which we keep in a ring buffer
    messageBufferSize:int

    # this is the list of the last messages
    lastMessages = []
    messageRingBufferCounter:int

    # this is the list of the reputation relevant roles
    reputationRoles = {}

    muteRole:discord.Role

    def __init__(self,
                theGuild:discord.Guild,
                messageBufferSize:int,
                muteRole:int) -> None:
        self.theGuild=theGuild
        self.messageBufferSize=messageBufferSize
        self.messageRingBufferCounter=0

        for role in theGuild.roles:
           if int(muteRole) == int(role.id):
               self.muteRole=role

    # ##########################################################
    # getReputation returns the reputation value for a given
    # user either as an int value or as a human readable
    # text version
    # ##########################################################


    def getReputation(self,discordUser:discord.Member,textValue:bool):

        # users get initial reputation based on age
        now=datetime.datetime.now().replace(tzinfo=None)
        userJoin=discordUser.joined_at.replace(tzinfo=None)
        userAge = now - userJoin

        theReputation=userAge.days
        theReputationText="Your Reputation:\n\nInitial (age): " + str(theReputation) + "\n"

        # calculate user's score based on reputation roles he/she is in

        r:ReputationRole
        for r in self.reputationRoles:
            theRole=discordUser.get_role(r)
            if not (theRole is None): 
                theReputation += self.reputationRoles[r].score
                theReputationText += "Role " + theRole.name + ": " + str(self.reputationRoles[r].score) + "\n"

        # add the penalties from the message buffer        

        messageCount=0
        linkCount=0
        m:MessageData
        for m in self.lastMessages:
            if discordUser == m.user:
                messageCount +=1
                if ('://' in m.Messagecontent):
                    linkCount +=1

        # calculate the remaining reputation credits and construct
        # the human readable version

        theReputation = theReputation + messageCount * self.messagePenalty
        theReputationText += "Message penalty: " + str(messageCount * self.messagePenalty) + "\n"
        theReputation = theReputation + linkCount * self.linkPenalty
        theReputationText += "Link usage penalty: " + str(linkCount * self.linkPenalty) + "\n"

        theReputationText += "\nTotal Reputation: " + str(theReputation) + "\n"

        if textValue == True:
            return(theReputationText)
        else:
            return(theReputation)

    # ##########################################################
    # addReputationRole adds a role that has reputation impact 
    # to the class
    # ##########################################################


    def addReputationRole(self,discordRoleID:int,roleScore:int):
        theNewRole=ReputationRole(discordRoleID,roleScore)
        self.reputationRoles[discordRoleID]=theNewRole

    # ##########################################################
    # checkMessage analyzes the Message ring buffer and checks
    # the user's remaining reputation credits
    # If the user reaches the Throttle limit then the user will
    # be warned after each message.
    # ignoring the warnings will lead to a MUTE role being
    # assigned to the user
    # ##########################################################

    async def checkMessage(self,newMessage:discord.Message):

        hasLink=False
        theNewMessage=MessageData(newMessage.content,newMessage.author)
        
        # add the new message to the ring buffer

        if len(self.lastMessages) < self.messageBufferSize:
            self.lastMessages.append(theNewMessage)
        else:
            self.lastMessages[self.messageRingBufferCounter]=theNewMessage
            self.messageRingBufferCounter +=1
            if self.messageRingBufferCounter >= self.messageBufferSize:
                self.messageRingBufferCounter =0

        # count the number of messages for that user in the ring buffer in order
        # to evaluate if we need to do a reputation check

        m:MessageData
        userMessageCount = sum(1 for m in self.lastMessages if m.user == newMessage.author)
        if userMessageCount >= self.triggerCheckThreshold:
            r = self.getReputation(newMessage.author,False)
            if r <= self.muteThreshold: 
                await newMessage.author.add_roles(self.muteRole)
                return(-1)
            if r <= self.throttleThreshold: return(0)
        return(1)
