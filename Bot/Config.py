from os import environ as env

class Telegram:
    API_ID = int(env.get("TG_API_ID", 27106563))
    API_HASH = env.get("TG_API_HASH", "bc347e85dfa4ce7cae0fe3479cda705f")
    BOT_TOKEN = env.get("TG_BOT_TOKEN", "6697056535:AAH-mF2_8OHzAAWH7U3YVRKvppzimFHpsHE")
    BOT_USERNAME = env.get("TG_BOT_USERNAME", "MovieTM0143_Bot")
    EMOJIS = [
        "👍", "👎", "❤", "🔥", 
        "🥰", "👏", "😁", "🤔",
        "🤯", "😱", "🤬", "😢",
        "🎉", "🤩", "🤮", "💩",
        "🙏", "👌", "🕊", "🤡",
        "🥱", "🥴", "😍", "🐳",
        "❤‍🔥", "🌚", "🌭", "💯",
        "🤣", "⚡", "🍌", "🏆",
        "💔", "🤨", "😐", "🍓",
        "🍾", "💋", "🖕", "😈",
        "😴", "😭", "🤓", "👻",
        "👨‍💻", "👀", "🎃", "🙈",
        "😇", "😨", "🤝", "✍",
        "🤗", "🫡", "🎅", "🎄",
        "☃", "💅", "🤪", "🗿",
        "🆒", "💘", "🙉", "🦄",
        "😘", "💊", "🙊", "😎",
        "👾", "🤷‍♂", "🤷", "🤷‍♀",
        "😡"
    ]

LOGGER_CONFIG_JSON = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s][%(name)s][%(levelname)s] -> %(message)s',
            'datefmt': '%d/%m/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'filename': 'event-log.txt',
            'formatter': 'default'
        },
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'loggers': {
        'bot': {
            'level': 'INFO',
            'handlers': ['file_handler', 'stream_handler']
        },
        'pyrogram': {
            'level': 'INFO',
            'handlers': ['file_handler', 'stream_handler']
        }
    }
}