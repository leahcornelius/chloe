import asyncio
import discord
from discord.ext import commands
from gtts import gTTS
from .utils import *
from random import randint
from time import sleep

logger = setup_logger(__name__)
turns = []

safeSpace = [741731467016667236, 677206266266910731, 821396094285905920,
             821456612627316796, 821355089792335912, 842837099945656343, 716823909051138068, 
             803045826196144161, 491256308461207575, 710608408406917180, 
             815058778008453142, 742383445333901394]
needMention = True
authorId = 634078084798349313
client = discord.Client()
history_dict = {}
global general_params
global device
global seed
global debug
global generation_pipeline_kwargs
global generator_kwargs
global prior_ranker_weights
global cond_ranker_weights
global chatbot_params
global max_turns_history
global generation_pipeline
global ranker_dict
number_of_sent_messages = 0
discord_token = "ODM3MzUwOTcyNDY0NDMxMTY1.YM3J9Q.Xz3xIlDzlYsLNxqdnJPwDjQ39z4"


def run(**kwargs):
    # Extract parameters
    global general_params
    global device
    global seed
    global debug
    global generation_pipeline_kwargs
    global generator_kwargs
    global prior_ranker_weights
    global cond_ranker_weights
    global chatbot_params
    global max_turns_history
    global generation_pipeline
    global ranker_dict
    global discord_token
    general_params = kwargs.get('general_params', {})
    device = general_params.get('device', -1)
    seed = general_params.get('seed', None)
    debug = general_params.get('debug', False)

    generation_pipeline_kwargs = kwargs.get('generation_pipeline_kwargs', {})
    generation_pipeline_kwargs = {**{
        'model': 'microsoft/DialoGPT-medium'
    }, **generation_pipeline_kwargs}

    generator_kwargs = kwargs.get('generator_kwargs', {})
    generator_kwargs = {**{
        'max_length': 1000,
        'do_sample': True,
        'clean_up_tokenization_spaces': True
    }, **generator_kwargs}

    prior_ranker_weights = kwargs.get('prior_ranker_weights', {})
    cond_ranker_weights = kwargs.get('cond_ranker_weights', {})

    chatbot_params = kwargs.get('chatbot_params', {})
    discord_token = chatbot_params.get('discord_token', 'none')
    max_turns_history = chatbot_params.get('max_turns_history', 2)

    # Prepare the pipelines
    generation_pipeline = load_pipeline(
        'text-generation', device=device, **generation_pipeline_kwargs)
    ranker_dict = build_ranker_dict(
        device=device, **prior_ranker_weights, **cond_ranker_weights)

    # Run the chatbot
    logger.info("Running the discord bot...")
    if (discord_token):
        client.run("ODM3MzUwOTcyNDY0NDMxMTY1.YM3J9Q.Xz3xIlDzlYsLNxqdnJPwDjQ39z4")
    else:
        logger.error("Failed to read discord token from config file")
        client.run(null)


@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))
    # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="(C97) [Studio KIMIGABUCHI (Kimimaru)] Gotoubun no Seidorei Side-C (Gotoubun no Hanayome)"))


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
    global device
    global seed
    global debug
    global generation_pipeline_kwargs
    global generator_kwargs
    global prior_ranker_weights
    global cond_ranker_weights
    global chatbot_params
    global max_turns_history
    global generation_pipeline
    global ranker_dict
    global turns
    global history_dict

    if max_turns_history == 0:
        # If you still get different responses then set seed
        turns = []

    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    str_channel_id = str(channel_id)
    # turns.append(turn)
    turn['user_messages'].append(prompt)
    if not channel_id in history_dict:
        history_dict[channel_id] = []

    history_dict[channel_id].append(turn)
    # Merge turns into a single history (don't forget EOS token)
    history = ""
    from_index = max(len(
        history_dict[channel_id])-max_turns_history-1, 0) if max_turns_history >= 0 else 0

    for i in range(len(history_dict[channel_id])):
        if(i >= from_index):
            turn2 = history_dict[channel_id][i]
        else:
            continue
        # Each turn begings with user messages
        for message in turn2['user_messages']:
            history += clean_text(message) + \
                generation_pipeline.tokenizer.eos_token
        for message in turn2['bot_messages']:
            history += clean_text(message) + \
                generation_pipeline.tokenizer.eos_token

    logger.info('User ({}): {}'.format(channel_id, prompt))
    logger.debug("CTX: {}".format(history))
    # Generate bot messages
    bot_messages = generate_responses(
        history,
        generation_pipeline,
        seed=seed,
        debug=debug,
        **generator_kwargs
    )
    if len(bot_messages) == 1:
        bot_message = bot_messages[0]
        logger.info('Bot: {}'.format(bot_message))
    else:
        bot_message = pick_best_response(
            prompt,
            bot_messages,
            ranker_dict,
            debug=debug
        )
        logger.debug("Generated responses: {}".format(bot_messages))
        logger.info('Bot ({}): {}'.format(channel_id, bot_message))
    turn['bot_messages'].append(bot_message)
    return bot_message
