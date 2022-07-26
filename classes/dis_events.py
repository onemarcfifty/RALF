import json
from classes.restfulapi import DiscordAPI

# #########################################################
# The class for Discord scheduled events
# as of 2022-07, discord.py does not support 
# scheduled Events. Therefore we need to use the Rest API
# #########################################################


class DiscordEvents(DiscordAPI):

#    def __init__(self, 
#                discord_token: str, 
#                client_id: str,
#                bot_permissions: int,
#                api_version: int) -> None:
#
#        super().__init__(discord_token,client_id,bot_permissions,api_version)


    async def list_guild_events(self,guild_id) -> list:

        # Returns a list of upcoming events for the supplied guild ID
        # Format of return is a list of one dictionary per event containing information.

        event_retrieve_url = f'{self.base_api_url}/guilds/{guild_id}/scheduled-events'
        response_list = await self.get_api(event_retrieve_url)
        return response_list

    async def create_guild_event(
        self,
        event_name: str,
        event_description: str,
        event_start_time: str,
        event_end_time: str,
        event_metadata: dict,
        event_privacy_level=2,
        channel_id=None,
        guild_id=0
    ) -> None:
        
        # Creates a guild event using the supplied arguments
        # The expected event_metadata format is event_metadata={'location': 'YOUR_LOCATION_NAME'}
        # We hard code Entity type to "2" which is Voice channel
        # hence we need no Event Metadata
        # The required time format is %Y-%m-%dT%H:%M:%S
        # Event times can use UTC Offsets! - if you omit, then it will be 
        # undefined (i.e. UTC / GMT+0)

        event_create_url = f'{self.base_api_url}/guilds/{guild_id}/scheduled-events'
        event_data = json.dumps({
            'name': event_name,
            'privacy_level': event_privacy_level,
            'scheduled_start_time': event_start_time,
            'scheduled_end_time': event_end_time,
            'description': event_description,
            'channel_id': channel_id,
            'entity_metadata': event_metadata,
            'entity_type': 2
        })
        try:
            await self.post_api(event_create_url,event_data)
        except Exception as e:
            print(f'DiscordEvents.createguildevent : {e}')
