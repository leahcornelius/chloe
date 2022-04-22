import discord
from .utils import *
from random import randint
from time import sleep
from api_client import ApiClient

logger = setup_logger(__name__)


safeSpace = [] # The bot will always repond in these channels, without needing a mention. Add one by sending "safe space" in the channel (or add it here)
needMention = True
authorId = 634078084798349313 # The owner of this bot, used for admin purposes and the bot will always respond to this account
client = discord.Client()
general_params=None
seed=None
debug=None
chatbot_params=None
max_turns_history=None
api_client=None
number_of_sent_messages = 0


def run(**kwargs):
    # Extract parameters
    global general_params
    global seed
    global debug
    global chatbot_params
    global max_turns_history
    global discord_token
    global api_client
    general_params = kwargs.get('general_params', {})
    seed = general_params.get('seed', None)
    debug = general_params.get('debug', False)
    chatbot_params = kwargs.get('chatbot_params', {})
    max_turns_history = chatbot_params.get('max_turns_history', 2)
    discord_token = chatbot_params.get('discord_token', None)
    # Connect to the API
    api_client = ApiClient("127.0.0.1:5000", "qwertybob_key01", "discord_bot")
    api_client.authenticate()

    # Run the chatbot
    logger.info("Running the discord bot...")
    if (discord_token):
        client.run(discord_token)
    else:
        logger.error("Failed to read discord token from config file")
        client.run(None)


@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))
    #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Netflix"))


@client.event
async def on_message(message):
    global needMention, authorId, safeSpace
    from datetime import datetime
    from random import randint
    from time import sleep
    global number_of_sent_messages, needMention
    from random import randrange
    # if (datetime.now().timestamp() - message.created_at.timestamp()) > 60:
    # logger.debug("msg too old")
    # return
    if randrange(0, 10) > 9:
        logger.debug("rand dropping")
        return
    if message.author == client.user:
        return
    if (message.author.id == authorId):
        # commands
        if (message.content == "needMention"):
            logger.info("No longer need mention globally")
        elif (message.content == "safe space"):
            safeSpace.append(message.channel.id)
            logger.info("Added " + str(message.channel.id) +
                        " to list of safe spaces")

    if(client.user.mentioned_in(message) or (isinstance(message.channel, discord.abc.PrivateChannel) and False) or needMention == False or message.channel.id in safeSpace or message.author.id == authorId):
        sleep(randint(1, 5))
        async with message.channel.typing():
            txtinput = message.content.replace("<@" + str(client.user.id) + ">", "").replace("<@!" + str(
                client.user.id) + ">", "")  # Filter out the mention so the bot does not get confused
            txt = ''
            if(isinstance(message.channel, discord.abc.PrivateChannel)):
                txt = get_response(txtinput, message.author.id,
                                   False)  # Get a response!
            else:
                txt = get_response(txtinput, message.channel.id,
                                   False)  # Get a response!
            number_of_sent_messages += 1
            from time import sleep

            sleep((len(txt) / 200) * 30)
#           print((message.created_at.timestamp() - datetime.now().timestamp()))
            bot_message = await message.channel.send(txt)  # Fire away!


def get_response(prompt, channel_id, do_infite):
    global general_params
    global debug
    global max_turns_history
    global api_client

    
    logger.info('User ({}): {}'.format(channel_id, prompt))
    bubble_id= "discord-{}".format(channel_id)
    if not api_client.bubble_exists(bubble_id):
        api_client.create_bubble("discord-{}".format(channel_id), max_turns_history)
    bot_message = api_client.get_response(prompt, bubble_id)
    return bot_message
