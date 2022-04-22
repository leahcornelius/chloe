import argparse

#from gpt2bot.telegram_bot import run as run_telegram_bot
from gpt2bot.utils import parse_config

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--type',
        type=str,
        default='discord',
        help="Type of the conversation to run: telegram, console, dialogue or discord (api must be running using the api option)"
    )
    arg_parser.add_argument(
        '--config',
        type=str,
        default='chatbot.cfg',
        help="Path to the config"
    )
    args = arg_parser.parse_args()
    config_path = args.config
    config = parse_config(config_path)

    if args.type == 'console':
        from gpt2bot.console_bot import run_console_bot
        run_console_bot(**config)
    elif args.type == 'dialogue':
        from gpt2bot.dialogue_bot import run_dialoge_bot
        run_dialoge_bot(**config)
    elif args.type == 'discord':
        from gpt2bot.discord_bot import run as run_discord_bot
        run_discord_bot(**config)
    elif args.type == 'api':
        from gpt2bot.api import run as api_run
        api_run(**config)
    else:
        raise ValueError("Unrecognized conversation type")
