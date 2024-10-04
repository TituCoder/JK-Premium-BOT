import re
from os import environ, getenv
from Script import script 

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '27106563'))
API_HASH = environ.get('API_HASH', 'bc347e85dfa4ce7cae0fe3479cda705f')
BOT_TOKEN = environ.get('BOT_TOKEN', '6697056535:AAGsGsYwyXy_NewmBfgZwJt0WAH-8NubcMA')
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")
# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled((environ.get('USE_CAPTION_FILTER', 'True')), True)

PICS = (environ.get('PICS', 'https://envs.sh/PL2.jpg')).split()
NOR_IMG = environ.get("NOR_IMG", "https://envs.sh/PL2.jpg" )
MELCOW_VID = environ.get("MELCOW_VID", "https://telegra.ph/file/451f038b4e7c2ddd10dc0.mp4")
SPELL_IMG = environ.get("SPELL_IMG", "https://telegra.ph/file/5e2d4418525832bc9a1b9.jpg")
VID = environ.get('VID', 'https://graph.org/file/943ab14a83315640f65e8.mp4')

# premium QR & PHOTO
SUBSCRIPTION = (environ.get('SUBSCRIPTION', 'https://telegra.ph/file/ffd0ce0182b0b94c57c53.jpg'))
CODE = (environ.get('CODE', 'https://telegra.ph/file/ffd0ce0182b0b94c57c53.jpg')) # Scanner Code image 

#refer time, or user count
REFERAL_USER_TIME = int(environ.get('REFERAL_USER_TIME', "2592000")) # set in seconds | already seted 1 month premium
USERS_COUNT = int(environ.get('USERS_COUNT', "10")) # Set Referel User Count
INVITED_USER_TRAIL = int(environ.get('INVITED_USER_TRAIL', "86400")) #set in seconds, free trail invites users in 1 day, 

#streming link shortner
STREAM_SITE = environ.get('IMPORT_JK_SITE', 'onepageyam.com')
STREAM_API = environ.get('IMPORT_JK_API', '70db509936f7f315fa550b241f50b24d00dc0c80')
JK_STREAM_MODE = is_enabled((environ.get('JK_STREAM_MODE', 'False')), False)
STREAMHTO = (environ.get('STREAMHTO', 'https://t.me/Jaynath_Backup_Channel/76'))

#premium Users Satuts
premium = environ.get('PREMIUM_LOGS', '-1002073485610')
PREMIUM_LOGS = int(premium) if premium and id_pattern.search(premium) else None
OWNER_USER_NAME = environ.get("OWNER_USER_NAME", "Owner0423_Bot") # widout 👉 @
CHECK_PREMIUM_FOR_QUALITY = is_enabled((environ.get('CHECK_PREMIUM_FOR_QUALITY', 'True')), True)
# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5069888600 6445840990').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002043695166 -1002055127272').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', "-1001883539506")
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
support_chat_id = environ.get('SUPPORT_CHAT_ID')
reqst_channel = environ.get('REQST_CHANNEL_ID')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
NO_RESULTS_MSG = is_enabled((environ.get("NO_RESULTS_MSG", 'True')), False)

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://jaynath0143:jaynath0143@cluster0.liw9lc8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "Jaynath")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# verify Shortener 
IS_VERIFY = is_enabled((environ.get('IS_VERIFY', 'False')), False)
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', "https://t.me/Jaynath_Backup_Channel/76")
VERIFY2_URL = environ.get('VERIFY2_URL', "onepageyam.com")
VERIFY2_API = environ.get('VERIFY2_API', "70db509936f7f315fa550b241f50b24d00dc0c80")
# how to open link
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/Jaynath_Backup_Channel/76')
IS_TUTORIAL = bool(environ.get('IS_TUTORIAL', True))

# files Shortner site
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'onepageyam.com')
SHORTLINK_API = environ.get('SHORTLINK_API', '70db509936f7f315fa550b241f50b24d00dc0c80')
IS_SHORTLINK = is_enabled((environ.get('IS_SHORTLINK', 'False')), False)

YEARS =  ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2002", "2001", "2000",]

DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-1002249135760').split()]
MAX_B_TN = environ.get("MAX_B_TN", "7")
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
PORT = environ.get("PORT", "8080")
GRP_LNK = environ.get('GRP_LNK','https://t.me/Jaynath_Movie_Request')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/Jaynath_Movie_Channel')
MSG_ALRT = environ.get('MSG_ALRT', '𝗠𝗿 𝗝𝗮𝘆𝗻𝗮𝘁𝗵⚡')
LOG_CHANNEL = int(environ.get('LOG_CHANNEL',  -1002073485610))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'Jaynath_Movie_Request')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "True")), True)
PM_FILTER = is_enabled((environ.get('PM_FILTER', "False")), False)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)
COMMAND_HAND_LER = environ.get("COMMAND_HAND_LER", "/")
TG_MAX_SELECT_LEN = environ.get("TG_MAX_SELECT_LEN", "100")
TMP_DOWNLOAD_DIRECTORY = environ.get("TMP_DOWNLOAD_DIRECTORY", "./DOWNLOADS/")
DOWNLOAD_LOCATION = environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS/AudioBoT/")

EMOJIS = [
        "👍", "❤️", "🔥", "👀",
        "🥰", "👏", "😎","🚀",
        "😱","😍","💥","✨",
        "🎉", "🤩","👌", "🕊",
        "❤️‍🔥", "💯", "⚡️", "✅", "👻",
        "😇","🤗", "💝","🥀",
        "🆒","😘","🌚","🎭",
        "🤪","🐬","☘️","🌼",
        "💙","🌻","🐰","😱"]

# Streaming
BIN_CHANNEL = environ.get("BIN_CHANNEL", "-1002073485610")
if len(BIN_CHANNEL) == 0:
    logging.error('BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)
MULTI_CLIENT = False
PORT = int(environ.get('PORT', 8080))
NO_PORT = bool(environ.get('NO_PORT', False))
APP_NAME = None
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = environ.get('APP_NAME')
else:
    ON_HEROKU = False
BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else APP_NAME+'.herokuapp.com'
URL = "https://{}/".format(FQDN) if ON_HEROKU or NO_PORT else \
    "https://{}:{}/".format(FQDN, PORT)
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
WORKERS = int(environ.get('WORKERS', '4'))
SESSION_NAME = str(environ.get('SESSION_NAME', 'LusiBot'))
MULTI_CLIENT = False
name = str(environ.get('name', 'Lusifilms'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = str(getenv('APP_NAME'))

else:
    ON_HEROKU = False
HAS_SSL=bool(getenv('HAS_SSL',False))
if HAS_SSL:
    URL = "https://{}/".format(FQDN)
else:
    URL = "https://{}/".format(FQDN)
REPO_OWNER = "JKDeveloperr"

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
