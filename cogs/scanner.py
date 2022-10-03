# #####################################
#
# a virustotal scanner cog
# listens for messages and scans URLs,
# domains and files
# 
# #####################################

from asyncore import loop
import hashlib
from discord.ext import commands
import discord
import re
import vt
import asyncio

# #####################################
#
# some return values and constants
#
# #####################################


stFile=1
stURL=2
stDomain=3

rvHarmless="harmless"
rvSuspicious="suspicious"
rvMalicious="malicious"
rvUnknown="unknown"


# #####################################
#
# Class definition
#
# #####################################

class Scanner(commands.Cog):

    vTotalAPIKEY=None
    vtClient = None

    # ############################################
    # init routine
    # ############################################

    def __init__(self, bot):
        self.bot = bot
        genericDomainString='[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)'
        self.domainRegExp=f'{genericDomainString}'
        self.urlRegExp   =f'(?:http|ftp|sftp)s?://{genericDomainString}'

    # ############################################
    # registervTotal creates the VirusTotal API
    # ############################################

    def registervTotal(self,vToken):
        self.vTotalAPIKEY = vToken


    # ##############################################################
    # getVerdict submits domains, URLS and/or files to Virustotal
    # for scan
    # ##############################################################
    
    async def getVerdict(self,vtObjectSring):
        vtInfo:vt.Object
        theVerdict=rvHarmless 
        try:
            vtInfo=await self.vtClient.get_object_async(vtObjectSring)
        except Exception as e:
            theVerdict=rvUnknown
            print(f"scanner vtInfo returned {e}")

        if (not theVerdict == rvUnknown):    
            vtInfoAnalysis=vtInfo.get("last_analysis_stats")
            print(f"scanner vtInfo returned {vtInfoAnalysis}")
            m=vtInfoAnalysis["malicious"]
            h=vtInfoAnalysis["harmless"]
            s=vtInfoAnalysis["suspicious"]
            if (s>h):
                theVerdict = rvSuspicious
            if (m>h):
                theVerdict = rvMalicious
        return theVerdict

    # ##############################################################
    # scan_message submits Attachments, URLs to getVerdict
    # ##############################################################

    async def scan_message(self,msg):

        if msg.author.id == self.bot.user.id:
            return

        # if we have not yet used the client or if the
        # client had been closed in between then we re-
        # open it

        if (self.vtClient is None):
            try:
                self.vtClient = vt.Client(self.vTotalAPIKEY)
            except Exception as e:
                print(f"Error in scan_message: {e}")
                return

        # check for domain names
        checkEntries=re.findall(self.domainRegExp,msg.content.replace("\n",""),re.IGNORECASE)
        if len(checkEntries) >0:
            for c in checkEntries:
                print("{} is a Domain".format(c))

        # check for links
        checkEntries=re.findall(self.urlRegExp,msg.content.replace("\n",""),re.IGNORECASE)
        if len(checkEntries) >0:
            for c in checkEntries:
                newMessage="**SECURITY WARNING**\nAll URLs are scanned\n"
                xmsg=await msg.reply(newMessage)
                print("{} is a URL".format(c))
                url_id = vt.url_id(c)
                theVerdict = await self.getVerdict(f"/urls/{url_id}")
                newMessage=f'{newMessage}\n>> Scan result: **{theVerdict}**\n'
                await xmsg.edit(content=newMessage)
                if (theVerdict==rvMalicious):
                    await xmsg.edit(content=f'**MESSAGE HAS BEEN REMOVED FOR SECURITY REASONS**\n')
                    await msg.delete()
                    # take further action
                    break
                print("URL Scan finished")
                if (not theVerdict==rvSuspicious):
                    await xmsg.delete()

        # check embedded files
        if len(msg.attachments) > 0:
            newMessage="**SECURITY WARNING**\nFiles posted here are systematically scanned\nEven if the scan is negative the file may still be malicious\n"
            xmsg=await msg.reply(newMessage)
            for theAttachment in msg.attachments:
                newMessage=f'{newMessage}\n>> hashing file {theAttachment.filename}'
                await xmsg.edit(content=newMessage)
                attachmentContent = await theAttachment.read()
                sha256String = hashlib.sha256(attachmentContent).hexdigest();
                newMessage=f'{newMessage}\n>> submitting hash to Scan Engine'
                await xmsg.edit(content=newMessage)
                theVerdict=await self.getVerdict(f'/files/{sha256String}')
                newMessage=f'{newMessage}\n>> Scan result: **{theVerdict}**\n'
                await xmsg.edit(content=newMessage)
                if (theVerdict==rvMalicious):
                    await xmsg.edit(content=f'**FILE HAS BEEN REMOVED FOR SECURITY REASONS**\n')
                    await msg.delete()
                    # take further action


    # #####################################
    # hook into edited messages
    # #####################################

    
    @commands.Cog.listener()
    async def on_raw_message_edit(self, rawdata: discord.RawMessageUpdateEvent):
        channel = await self.bot.fetch_channel(rawdata.channel_id)
        try:
            msg = await channel.fetch_message(rawdata.message_id)
        except Exception as e:
            # message has been deleted by the scanner
            return
        if msg.author.id == self.bot.user.id:
            return
        asyncio.create_task(self.scan_message(msg))
        #await self.scan_message(msg)

    # #####################################
    # hook into new messages
    # #####################################
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.user.id:
            return
        asyncio.create_task(self.scan_message(msg))

# #####################################
# The cog init
# #####################################

async def setup(bot):
    await bot.add_cog(Scanner(bot))
