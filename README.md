# R.A.L.F. is a discord-bot

R.A.L.F. (short for Responsive Artificial Lifeform ;-) ) is the "housekeeping" bot on the oneMarcFifty Discord Server

It can do the following things (release version 0.2):

- reply with "pong" to a "ping" (WHOA!!!)
- Send out configurable random messages when the server is idle (like "Did you know...")
- automatically create Events (we have Sunday video sessions at 9 AM and 6 PM)
- remind subscribers of upcoming events

Planned (release 0.3)

- Help the user create a support thread with a modal view
- let the user subscribe / unsubscribe to notification messages with a modal view

## How to use

You need the discord.py wrapper from Rapptz :

    git clone https://github.com/Rapptz/discord.py
    cd discord.py/
    python3 -m pip install -U .[voice]

Next, adapt the `secret.py` file to reflect your token etc.
Also, customize all settings in `config.py` and the text files in the
`bot_messages`directory

Now you can cd into the bot's directory and launch it with

    python3 main.py
