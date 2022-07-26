# R.A.L.F. is a discord-bot

R.A.L.F. (short for Responsive Artificial Lifeform ;-) ) is the "housekeeping" bot on the oneMarcFifty Discord Server

It can do the following things (release version 0.4):

- reply with "pong" to a "ping" (WHOA!!!)
- Send out configurable random messages when the server is idle (like "Did you know...")
- automatically create Events (we have Sunday video sessions at 9 AM and 6 PM)
- remind subscribers of upcoming events
- let the user subscribe / unsubscribe to notification messages with a modal view

## How to use

You need the discord.py wrapper from Rapptz :

    git clone https://github.com/Rapptz/discord.py
    cd discord.py/
    python3 -m pip install -U .[voice]

Next, adapt the `config.json` file to reflect your token etc.

Now you can cd into the bot's directory and launch it with

    python3 main.py

## slash commands

The bot supports the following commands:
- **/setup** set up basic functionality (channel for idle messages, frequency of the messages, channel that contains the templates)
- **/subscribe** let a user subscribe to roles that are defined in the scheduled events
- **/update** update the bot (re-read the template channel)
- **/say_ralf** let ralf say something. You can specify the channel and the message ;-)

## How do you configure R.A.L.F. ?

First you need a minimum `config.json`like shown in `minimum.config.json` that contains your token and client id.

All other values are taken from a "Template" channel. When you run the **/setup** command, R.A.L.F. will let you chose that one.

In that template channel, you just create messages that you want R.A.L.F. to send randomly into the configured idle_channel.

### how to configure Events ?

A special type of template message contains a definition of scheduled events. The message needs to contain data that can be converted to a dict object, like this:

    {
        "title": "Sunday Funday session (PM)",
        "description": "Chat with Marc and the folks here on the server ! Share your screen if you want to walk through a problem. Talk about tech stuff with the other members or just listen in...",
        "channel": 12345452435,
        "notify_hint": "get notified when the PM session starts",
        "subscription_role_num": 12432345423,
        "notify_minutes": 30,
        "day_of_week": 6,
        "start_time": "18:00:00",
        "end_time": "19:00:00"
    } 

(when you use the /update command, it will tell you if it could read it or not.)
Every Monday, R.A.L.F. will then go through the Events and create them as scheduled events on the guild/server.

If the user has the `subscription_role_num` role, then he/she will be notified by R.A.L.F. roughly `notify_minutes`before the event starts.

### What's the story behind R.A.L.F. ?

My son (who is studying computer science) came up to me and said it would be nice if we did a coding project together. I then thought this over and also wanted it to be something usable. On my discord server, there are a couple of things that I keep forgetting, such as generating the scheduled events or reminding people that the Sunday Funday! session had started. I told him "let's start with a simple ping bot that replies with pong. But you will see, I will have it done faster than you!" - 30 minutes later he called me up and showed me the working thing - I hadn't even started ;-)
He has contributed to this bot and the support bot (which you can find here on my Github as well) a lot, namely the /subscribe function and the question screening function

**enjoy!**
