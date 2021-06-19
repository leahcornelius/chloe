import discord
from gtts import gTTS
from .utils import *

logger = setup_logger(__name__)
turns = []


needMention = False
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
discord_token = "ODM3MzUwOTcyNDY0NDMxMTY1.YIrSHg.pqEdapAOyPLHZDrHzaeKXcnf96s"

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
        client.run("ODM3MzUwOTcyNDY0NDMxMTY1.YIrSHg.pqEdapAOyPLHZDrHzaeKXcnf96s", bot = False)
    else:
        logger.error("Failed to read discord token from config file")
        client.run(null)


@client.event
async def on_ready():
     logger.info('We have logged in as {0.user}'.format(client))
     #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="(C97) [Studio KIMIGABUCHI (Kimimaru)] Gotoubun no Seidorei Side-C (Gotoubun no Hanayome)"))

@client.event
async def on_message(message):
    from datetime import datetime
    global number_of_sent_messages, needMention
    from random import randrange
    if (datetime.now().timestamp() - message.created_at.timestamp()) > 60:
       return
    elif randrange(0, 10) > 9:
       return
    if message.author == client.user:
        return    
    if(message == "playwithleoscock"):
        voice_channel=user.voice.voice_channel
        channel=None
        # only play music if user is in a voice channel
        if voice_channel!= None:
            # grab user's voice channel
            channel=voice_channel.name
            # create StreamPlayer
            vc= await client.join_voice_channel(voice_channel)
            tts = gTTS('your nan lol')
            tts.save("nan.mp3")
            player = vc.create_ffmpeg_player('nan.mp3', after=lambda: print('done'))
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)
            # disconnect after the player has finished
            player.stop()
            await vc.disconnect()
        else:
            await message.channel.send('NO u')
    from random import randint
    from time import sleep

    sleep(randint(3,10))
    if(client.user.mentioned_in(message) or isinstance(message.channel, discord.abc.PrivateChannel) or needMention == False):
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
#          print((message.created_at.timestamp() - datetime.now().timestamp()))
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
    #turns.append(turn)
    turn['user_messages'].append(prompt)
    if not channel_id in history_dict:
        history_dict[channel_id] = []
    
    
    history_dict[channel_id].append(turn)
    # Merge turns into a single history (don't forget EOS token)
    history = ""
    from_index = max(len(history_dict[channel_id])-max_turns_history-1, 0) if max_turns_history >= 0 else 0

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
    logger.debug("CTX: {}".format(history));
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
        logger.debug("Generated responses: {}".format(bot_messages));
        logger.info('Bot ({}): {}'.format(channel_id, bot_message))
    turn['bot_messages'].append(bot_message)
    return bot_message



