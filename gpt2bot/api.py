# Copyright (c) 2020 Leo Cornelius
#  Licensed under the MIT license.
from flask import render_template
import flask
from flask_cors import CORS, cross_origin
from flask_ngrok import run_with_ngrok
from .utils import *

logger = setup_logger(__name__)
turns = []



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
run_with_ngrok(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True


admin_users = ['leocornelius', 'nathanarnold']


# Serve React App
@app.route('/')
def my_index():
    return render_template("index.html")
# Serve React App
@app.route('/script.js')
def my_js():
    return app.send_static_file('script.js')

@app.route('/get_response/<user_msg>', methods=['GET'])
@cross_origin()
def get_response(user_msg):
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
    prompt = user_msg
    print("User >>> {}".format(prompt))
    logger.info('User:', prompt)
    if (max_turns_history == 0 or prompt.lower() == "reset"):  # eg if she should have no memory
        turns = []

    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    turns.append(turn)
    turn['user_messages'].append(prompt)
    # Merge turns into a single prompt (don't forget delimiter)
    prompt = ""
    from_index = max(len(turns) - max_turns_history - 1,
                     0) if max_turns_history >= 0 else 0

    for turn in turns[from_index:]:
        # Each turn begins with user messages
        for user_message in turn['user_messages']:
            prompt += clean_text(user_message) + \
                generation_pipeline.tokenizer.eos_token
        for bot_message in turn['bot_messages']:
            prompt += clean_text(bot_message) + \
                generation_pipeline.tokenizer.eos_token

    # Generate bot messages
    bot_messages = generate_responses(
        prompt,
        generation_pipeline,
        seed=seed,
        debug=debug,
        **generator_kwargs
    )
    if len(bot_messages) == 1:
        bot_message = bot_messages[0]
        logger.info('Bot (S): {}'.format(bot_message))
    else:
        bot_message = pick_best_response(
            prompt,
            bot_messages,
            ranker_dict,
            debug=debug
        )
        logger.info('Bot (BR): {}'.format(bot_message))
    turn['bot_messages'].append(bot_message)
    return bot_message





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
    

    app.run()



