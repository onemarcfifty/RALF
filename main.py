import classes.bot as bot
import config

if config.cfg is None:
    config.readConfig()

client = bot.OMFClient()
client.run(config.SECRETS["BOT_TOKEN"])
