import discord
import traceback
import config

# ############################################
# the Support() class is a modal ui dialog
# that helps you create a thread in a 
# selected channel. It asks for a title
# and a description and then creates
# a Thread in the config.CONFIG["SUPPORT_CHANNEL_ID"]
# channel. It also sends a message to the
# config.CONFIG["IDLE_MESSAGE_CHANNEL_ID"]
# in order to notify everyone that a
# new support message has been created
# ############################################


class Support(discord.ui.Modal, title='Open a support thread'):

    # This will be a short input, where the user can enter a title
    # for the new thread 

    theTitle = discord.ui.TextInput(
        label='Title',
        placeholder='a catchy title for the issue',
    )

    # This is a longer, paragraph style input, where user can submit 
    # a description of the problem

    theDescription = discord.ui.TextInput(
        label='Describe the problem',
        style=discord.TextStyle.long,
        placeholder='Type in what the problem is...',
        required=False,
        max_length=300,
    )

    # ############################################
    # on_submit is called when the user submits the
    # Modal. This is where we create the thread
    # and send all related messages
    # ############################################

    async def on_submit(self, interaction: discord.Interaction):

        # first let's find out which channel we will create the thread in
        theGuild = interaction.guild
        theChannel : discord.TextChannel
        theChannel = theGuild.get_channel(config.CONFIG["SUPPORT_CHANNEL_ID"])

        if not (theChannel is None):
            try:
                # we send a message into that channel that serves as "hook" for the thread
                # (if we didn't have a message to hook then the thread would be created
                # as private which requires a boost level)

                xMsg= await theChannel.send (f"Support Thread for <@{interaction.user.id}>")
                newThread=await theChannel.create_thread(name=f"{self.theTitle.value}",message=xMsg,auto_archive_duration=1440)

                # next we want to post about the new "ticket" in the IDLE_MESSAGE_CHANNEL

                theChannel = theGuild.get_channel(config.CONFIG["IDLE_MESSAGE_CHANNEL_ID"])
                if (not (theChannel is None)) and (not (newThread is None)):
                    xMsg= await theChannel.send (f'I have created a **Support Thread** on behalf of <@{interaction.user.id}> :\n\n <#{newThread.id}> in the <#{config.CONFIG["SUPPORT_CHANNEL_ID"]}>\n\nMaybe you could check in and see if **you** can help ??? \nMany thanks !')
                    xMsg= await newThread.send (f'<@{interaction.user.id}> describes the problem as follows: \n{self.theDescription.value} \n \n please tag the user on your reply - thank you!' )
            except Exception as e:
                print(f"Support Error: {e}")

        # last but not least we send an ephemeral message to the user
        # linking to the created thread

        await interaction.response.send_message(f'Your Support Thread has been created here: <#{newThread.id}> Please check if everything is correct.\nThank you for using my services!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)
