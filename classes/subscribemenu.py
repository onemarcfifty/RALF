import discord
import traceback

from numpy import array
from classes.config import Config

# ############################################
# the Subscribe() class is a modal ui dialog
# that let's you select one or multiple
# roles that will be assigned to you.
# The roles are set in the config.AUTO_EVENTS
# variable
# ############################################


class SubscribeView(discord.ui.View):
    def __init__(self, autoEvents : array,member:discord.Member):
        super().__init__(timeout=180)
        self.add_item(SubscribeMenu(autoEvents=autoEvents,member=member))

class SubscribeMenu(discord.ui.Select):
    

    def __init__(self, autoEvents : array,member:discord.Member) -> None:

        # create the menu items from the Event roles:
        menu_options = []
        for menu_option in autoEvents:
            menu_options.append(discord.SelectOption(
                label= menu_option["notify_hint"],
                value=menu_option["subscription_role_num"]))

        # Make sure the existing user roles are preselected
        for option in menu_options:
            role = option.value
            if not (member.get_role(role) is None):
              option.default=True

        super().__init__(placeholder="Select your subscription",max_values=len(autoEvents),min_values=0,options=menu_options)

    

    async def callback(self, interaction: discord.Interaction):
        role: discord.Role
        roles = interaction.user.guild.roles
        member: discord.Member
        member = interaction.user

        # first we remove all roles
        for option in self.options:
            option.default=False
            introle=int(option.value)
            role=member.get_role(introle)
            if not (role is None):
                await member.remove_roles(role)

        # then we assign all selected roles
        # unfortunately we need to loop through all rolles
        # maybe there is a better solution ?
        for value in self.values:
            for role in roles:
                if int(value) == int(role.id):
                    await member.add_roles(role)
                    for option in self.options:
                        if int(option.value) == int(value):
                            option.default=True

        await interaction.response.send_message(content="Updated your subscriptions!",ephemeral=True)
        
                                                            

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)
