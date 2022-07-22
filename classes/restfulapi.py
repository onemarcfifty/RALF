import json
import aiohttp

# #########################################################
# The class for Discord API integration
# this can be used if certain functions are not supported
# by discord.py
# #########################################################

class DiscordAPI:

    # the init constructor stores the authentication-relevant data
    # such as the token and the bot url

    # guild ID, Client ID, Token, Bot permissions, API Version

    def __init__(self, 
                discord_token: str, 
                client_id: str,
                bot_permissions: int,
                api_version: int) -> None:

        self.base_api_url = f'https://discord.com/api/v{api_version}'
        self.bot_url = f'https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={bot_permissions}&scope=bot'
        self.auth_headers = {
            'Authorization':f'Bot {discord_token}',
            'User-Agent':f'DiscordBot ({self.bot_url}) Python/3.9 aiohttp/3.8.1',
            'Content-Type':'application/json'
        }

    # get_api does an https get on the api
    # it expects json data as result 

    async def get_api(self, api_url: str) -> list:

        async with aiohttp.ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.get(api_url) as response:
                    response.raise_for_status()
                    assert response.status == 200
                    response_list = json.loads(await response.read())
            except Exception as e:
                print(f'get_api EXCEPTION: {e}')
            finally:
                await session.close()
        return response_list

    # post_api does an https put to the api url
    # it expects json data as var which it posts

    async def post_api(self, api_url: str, dumped_jsondata: str) -> None:

        async with aiohttp.ClientSession(headers=self.auth_headers) as session:
            try:
                async with session.post(api_url, data=dumped_jsondata) as response:
                    response.raise_for_status()
                    assert response.status == 200
            except Exception as e:
                print(f'post_api EXCEPTION: {e}')
            finally:
                await session.close()