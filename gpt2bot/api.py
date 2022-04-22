# Copyright (c) 2020 Leo Cornelius
#  Licensed under the MIT license.
import string
import time
from flask import render_template
import flask
from flask_cors import CORS, cross_origin
from .utils import *

logger = setup_logger(__name__)
bubbles = {}
auth_tokens = []
passcode = "qwertybob_key01"

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


app = flask.Flask(__name__, static_folder="UI/dist", template_folder="UI/dist")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True

@app.route('/')
def my_index():
    return render_template("index.html")

@app.route("/auth/<device_id>/<tried_passcode>")
@cross_origin()
def auth(device_id, tried_passcode):
    global passcode, auth_tokens
    if tried_passcode != passcode:
        time.sleep(2)
        return "{\"error\": 2}" # Incorrect passcode
    else:
        token = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
        print("new device: {}, token: {}".format(device_id, token))
        auth_tokens.append(token)
        return "{\"token\":" + "\"{}\"".format(token) + "}"
@app.route('/get_response/<prompt>/<bubble_id>/<auth_token>', methods=['GET'])
@cross_origin()
def get_response(prompt, bubble_id, auth_token):
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
    global auth_tokens
    global bubbles
    if auth_token not in auth_tokens:
        return "{\"error\": 0}" # not authenticated
    elif bubble_id not in bubbles:
        print("Bubble {} not in bubble list, bubbles: ".format(bubble_id))
        for bubble in bubbles:
            print(bubble)
        return "{\"error\": 1}" # bubble does not exist

    print("User ({}) >>> {}".format(bubble_id, prompt))
    
    if (bubbles[bubble_id]["max_turns_history"] == 0 or prompt.lower() == "reset"):  # eg if she should have no memory
        bubbles[bubble_id]["history"] = []

    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [prompt],
        'bot_messages': []
    }
    bubbles[bubble_id]["history"].append(turn)
    # Merge turns into a single prompt (don't forget delimiter)
    prompt = ""
    from_index = max(len(bubbles[bubble_id]["history"]) - max_turns_history - 1,
                     0) if bubbles[bubble_id]["max_turns_history"] >= 0 else 0

    for turn in bubbles[bubble_id]["history"][from_index:]:
        # Each turn begins with user messages
        for user_message in turn['user_messages']:
            prompt += clean_text(user_message) + \
                generation_pipeline.tokenizer.eos_token
        for bot_message in turn['bot_messages']:
            prompt += clean_text(bot_message) + \
                generation_pipeline.tokenizer.eos_token

    # Generate bot messages
    logger.info("Context: {}".format(prompt))
    bot_messages = generate_responses(
        prompt,
        generation_pipeline,
        seed=seed,
        debug=debug,
        **generator_kwargs
    )
    if len(bot_messages) == 1:
        bot_message = bot_messages[0]
        logger.info('Bot ({}): {}'.format(bubble_id, bot_message))
    else:
        bot_message = pick_best_response(
            prompt,
            bot_messages,
            ranker_dict,
            debug=debug
        )
        logger.info('Bot (best response) ({}): {}'.format(bubble_id, bot_message))
    turn['bot_messages'].append(bot_message)
    return "{\"response\":" + " \"{}\"".format(bot_message) + "}"

@app.route('/create_bubble/<bubble_id>/<max_turns_history>/<auth_token>', methods=['GET'])
@cross_origin()
def create_bubble(bubble_id, max_turns_history, auth_token):
    if auth_token not in auth_tokens:
        print("Token {} not in list, tokens:".format(auth_token))
        for token in auth_tokens:
            print(token)
        return "{\"error\": 0}" # not authenticated
    elif bubble_id in bubbles:
        return "{\"error\": 3}" # bubble already exists
    else:
        bubbles[bubble_id] = {
            "max_turns_history": int(max_turns_history),
            "history": [] # TODO: permant memories via param
        }
        return "{\"bubble_id\": " + "\"{}\"".format(bubble_id) + "}"



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
    max_turns_history = chatbot_params.get('max_turns_history', 2)

    # Prepare the pipelines
    generation_pipeline = load_pipeline(
        'text-generation', device=device, **generation_pipeline_kwargs)
    ranker_dict = build_ranker_dict(
        device=device, **prior_ranker_weights, **cond_ranker_weights)

    # Run the api
    logger.info("Running the api...")
    

    app.run(host='0.0.0.0', debug=True)



