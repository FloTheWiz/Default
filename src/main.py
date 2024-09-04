from bot import Bot
from core.arghandler import make_parser, parse_logic


BOT_CONFIG = {
    'token':"YOUR_BOT_TOKEN_HERE",
    'prefix':'-',
    'cogs':[],
    'version_str':'0.1',
    'description': 'Testing bot',
    'activity': 'Testing bot',
}

if __name__ == '__main__':
    parser = make_parser()
    config = parse_logic(parser, BOT_CONFIG)
    if config == 0:
        exit(0)
    bot = Bot(config)
    bot.run(config['token'])