import argparse

from gpt2bot.telegram_bot import run as run_telegram_bot
from gpt2bot.console_bot import run as run_console_bot
from gpt2bot.discord_bot import run as run_discord_bot
from gpt2bot.dialogue import run as run_dialogue
from gpt2bot.utils import parse_config
from gpt2bot.api import run as api_run

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--type',
        type=str,
        default='discord',
        help="Type of the conversation to run: telegram, console, dialogue or discord"
    )
    arg_parser.add_argument(
        '--config',
        type=str,
        default='default_config.cfg',
        help="Path to the config"
    )
    args = arg_parser.parse_args()
    config_path = args.config
    config = parse_config(config_path)

    if args.type == 'telegram':
        run_telegram_bot(**config)
    elif args.type == 'console':
        run_console_bot(**config)
    elif args.type == 'dialogue':
        run_dialogue(**config)
    elif args.type == 'discord':
        run_discord_bot(**config)
    elif args.type == 'api':
        api_run(**config)
    else:
        raise ValueError("Unrecognized conversation type")
