
# Chloe AI
ChloeAI is a [DialoGPT](https://arxiv.org/abs/1911.00536) powered bot. [DialoGPT](https://arxiv.org/abs/1911.00536) is a large pretrained diologue generation model based on GPT2. It was trained by microsoft using 147M mullti-turn diolgue from redit. 

## Running
Chloe requires python 3.6+, please check your python version with `python3 --version`
All of chloes python libaries are in the `requirements.txt` file, you can install them with:
``python3 -m pip install -r requirements.txt``
You can then edit the config file, `default_config.cfg`  to your need

To run the bot run:
``python3 run_bot.py --type=discord``
Availble types are:
- discord - A discord bot
- telegram - A telegram bot
- dialouge - Where the bot will speak to itself
- api - Where the bot will open a REST api for usage with the UI
- omegle - TODO: the bot will connect with random people on omegle chat and talk to them, saving converstaions to a file. This is fun
  
## Configs

* [medium-cpu.cfg](https://github.com/leocornelius/chloe-ranked/blob/master/configs/medium-cpu.cfg): Medium model, no ranking (CPU)
* [large-gpu.cfg](https://github.com/leocornelius/chloe-ranked/blob/master/configs/large-gpu.cfg): Large model, no ranking (GPU)
* [large-updown-gpu.cfg](https://github.com/leocornelius/chloe-ranked/blob/master/configs/large-updown-gpu.cfg): Large model, `updown` ranker (GPU)
* [large-ensemble-gpu.cfg](https://github.com/leocornelius/chloe-ranked/blob/master/configs/large-ensemble-gpu.cfg): Large model, ensemble of 5 rankers (GPU, >12GB RAM)
* 
## Todo

I am currently working on adding LTSM (Long short-term memory) to provide the bot with a better short term memory. The idea is to create a seccond NLP foucosed model that will extract important statements from both the user and the bot and store them. This will then influence the bots decison. Such a model would take the following statement from the user and answer from the bot:
```
USER: God, i just love ice cream
BOT: Ew, i hate ice cream
```
And extract that:
- The user likes ice cream
- The bot hates ice cream
It would then add this to a database:
```
User.db
table_likes:
key: ice creame, context:None
Bot.db
table_dislikes
key: ice creme, context: Hates
```
If that user was to poll in the future "Do you like ice cream", the bot would respond simmilar to:
``No i hate it``. While the bot likes & dislikes will persit between each user to develop personailty, the users will get a DB of their own, using their discord id as an example. In a group context (eg discord server) when checking if a user does like something it will look in the db of the author.

This should provide somewhat effective long term memory, though how to inject these likes and dislikes without causing odd statments (for example if the bot hates cats but likes "eating ice cream" it may respond with "I love eating hate cats"). There will likley need to be anther model that decides which likes and dislikes need to be got from the DB. 

## Quality
When doing a single turn turing test (one question asked to the bot, a single answer given) it passes with high results. However, due to a lack of long range memory the conversation quickly degrades. Please see the todo secion on how i am trying to mitigate this
### DSTC-7 challenge

The dialoGPT model achieved the state-of-the-art results in [DSTC-7 Challenge response generation task](https://github.com/mgalley/DSTC7-End-to-End-Conversation-Modeling). 


| Experiment         | NIST2 | NIST4 | BLEU2  | BLEU4 | METEOR | ENT-4 | DIST-1 | DIST-2 | Avg. Len |
|--------------------|-------|-------|--------|-------|--------|----------|------------|------------|---------|
| Human response     | 2.62  | 2.65  | 12.35% | 3.13% | 8.31%  | 10.45    | 16.66%     | 67.01%     | 18.8    |
| DSTC-7 Winner      | 2.51  | 2.52  | 14.35% | 1.83% | 8.07%  | 9.03     | 10.89%     | 32.49%     | 15.1    |
| DialoGPT 345M      | 2.80  | 2.82  | 14.16% | 2.31% | 8.51%  | **10.08**    | 9.13%      | 39.73%     | 16.9    |
| DialoGPT 345M (BS) | **2.92**  | **2.97**  | **19.18%** | **6.05%** | **9.29%**  | 9.57     | **15.73%**     | **51.03%**     | 14.2    |

where ENT represents the [Entropy score](https://arxiv.org/abs/1809.05972), and DIST represents the [Distinct score](https://arxiv.org/pdf/1510.03055.pdf). For all metrics except the average length, larger are better.  

<!--| Experiment           | NIST1  | NIST2  | NIST3  | NIST4  | BLEU1  | BLEU2  | BLEU3  | BLEU4  | METEOR | ENT-1 | ENT-2 | ENT-3 | ENT-4 | DIST-1 | DIST-2 | Len |
|----------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|----------|----------|----------|----------|------------|------------|---------|
| Human                | 2.4237 | 2.6244 | 2.6472 | 2.65   | 0.3408 | 0.1235 | 0.0572 | 0.0313 | 0.0831 | 6.5893   | 9.7423   | 10.4101  | 10.4450  | 0.1666     | 0.6701     | 18.7568 |
| DSTC-7 Winner | 2.3408 | 2.5102 | 2.522  | 2.523  | 0.4122 | 0.1435 | 0.0501 | 0.0183 | 0.0807 | 5.3832   | 7.6065   | 8.5304   | 9.0298   | 0.1089     | 0.3249     | 15.1327 |
| DialoGPT           | 2.5863 | 2.804  | 2.823  | 2.8246 | 0.3927 | 0.1416 | 0.0555 | 0.0231 | 0.0851 | 5.5791   | 8.5109   | 9.6872   | 10.0765  | 0.0913     | 0.3973     | 16.9484 |
| DialoGPT(beam search)       | **2.5943**| **2.9163** | **2.9624** | **2.9681**| **0.4238** | **0.1918** | **0.1027** | **0.0605** | **0.0929** | **6.0815**   | **8.7379**   | 9.4037   | 9.5697   | 0.1573     | 0.5103     | 14.1603 |-->

Note that the superior automatic evaluation comparing to human responses does not necessary imply that the model achieves human parity. Please check out their paper for more detailed analysis.

## Credits
- Thank you to [polakowo](https://github.com/polakowo) for creating the [decoder](https://github.com/polakowo/gpt2bot) for dialoGPT
- Thank you to Microsoft for creating the underlying dialoGPT model ([paper](https://arxiv.org/abs/1911.00536), [repo](https://github.com/microsoft/DialoGPT)
- Leo Cornelius, developing the interfaces and POC-LSTM.
