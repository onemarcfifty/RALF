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

class Subscribe(discord.ui.Modal, title='(un)subscribe to Event-Notification'):
    

    def __init__(self, autoEvents : array,member:discord.Member) -> None:
        super().__init__()

        # create the menu items from the Event roles:
        menu_options = []
        for menu_option in autoEvents:
            menu_options.append(discord.SelectOption(
                label= menu_option["notify_hint"],
                value=menu_option["subscription_role_num"]))

        # define the UI dropdown menu Element
        self.Menu = discord.ui.Select(
            options = menu_options,
            max_values=len(autoEvents),
            min_values=0)

        # Make sure the existing user roles are preselected
        for option in self.Menu.options:
            role = option.value
            if not (member.get_role(role) is None):
              option.default=True

        # now add the child element to the form for drawing
        self.add_item(self.Menu)
    

    # #####################################
    # on_submit is called when the user submits
    # the modal. It will then go through
    # the menu options and revoke / assign
    # the corresponding roles
    # #####################################
    

    async def on_submit(self, interaction: discord.Interaction):
        role: discord.Role
        roles = interaction.user.guild.roles
        member: discord.Member
        member = interaction.user
        
        # first we remove all roles
        for option in self.Menu.options:
            role=member.get_role(option.value)
            if not (role is None):
                await member.remove_roles(role)

        # then we assign all selected roles
        # unfortunately we need to loop through all rolles
        # maybe there is a better solution ?
        for option in self.Menu._selected_values:
            for role in roles:
                if int(option) == int(role.id):
                    await member.add_roles(role)


        await interaction.response.send_message(f'Thanks for using my services !', ephemeral=True)

                                                            

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)
