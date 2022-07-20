# the amount of seconds that the channel needs to be idle 
# before the bot posts a generic "did you know" 
# message

CHANNEL_IDLE_INTERVAL: int = 7200

# the name of the directory where the text files are
# located which contain the messages
# which the bot will randomly send
#  (1 file = 1 message)

IDLE_MESSAGE_DIR: str = "bot_messages"

# the channel where the bot will post messages to

IDLE_MESSAGE_CHANNEL_ID = 758271650226765848

#Variable that indicates when the bot answers after a question has been asked
#(in seconds)

SLEEPING_TIME = 10

# The subscription roles and their meaning

SUBSCRIPTION_TEXT = ['get notified when the AM session starts','get notified when the PM session starts']
SUBSCRIPTION_ROLES = ['notify_am','notify_pm']
