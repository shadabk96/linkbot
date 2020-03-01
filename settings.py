import importlib
import sys
import os

DEBUG = False

PLUGINS = [
    'linkbot.plugins',
]
PLUGINS_ONLY_DOC_STRING = False

# Default settings
MATTERMOST_API_VERSION = 4
BOT_URL = 'http://localhost:8065/api/v4'
# BOT_LOGIN = 'bot@example.com'
# BOT_PASSWORD = None
BOT_TOKEN = "y8aej34o5pnjjbx6cmapxuqpfo"
BOT_TEAM = 'hack20'
SSL_VERIFY = False
WS_ORIGIN = None
WEBHOOK_ID = None  # if not specified linkbot will attempt to create one

IGNORE_NOTIFIES = ['@here', '@channel', '@all']
IGNORE_USERS = []
WORKERS_NUM = 10

DEFAULT_REPLY_MODULE = None
DEFAULT_REPLY = None

"""
If you use Mattermost Web API to send messages (with send_webapi()
or reply_webapi()), you can customize the bot logo by providing Icon or Emoji.
If you use Mattermost API to send messages (with send() or reply()),
the used icon comes from bot settings and Icon or Emoji has no effect.
"""
# BOT_ICON = 'http://lorempixel.com/64/64/abstract/7/'
# BOT_EMOJI = ':godmode:'

"""
Period to trigger jobs in sechduler. Measures in seconds.
If JOB_TRIGGER_PERIOD is not set, linkbot will set default priod 5 seconds.
"""
JOB_TRIGGER_PERIOD = 5

"""
Load local settings
"""
for key in os.environ:
    if key[:15] == 'MATTERMOST_BOT_':
        globals()[key[11:]] = os.environ[key]

settings_module = os.environ.get('MATTERMOST_BOT_SETTINGS_MODULE')

if settings_module is not None:
    pwd = os.getcwd()
    if pwd not in sys.path:
        sys.path.insert(0, pwd)
    settings = importlib.import_module(settings_module)
    filename = settings.__file__.replace('.pyc', '.py')
    try:
        execfile(filename)
    except NameError:
        exec(open(filename, encoding='utf-8').read())

try:
    from linkbot_settings import *  # noqa: F401, F403
except ImportError:
    try:
        from local_settings import *  # noqa: F401, F403
    except ImportError:
        pass
