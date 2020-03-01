# linkbot
mattermost hackathon entry

[![Python Support](https://img.shields.io/pypi/pyversions/mmpy-bot.svg)](https://pypi.org/project/mmpy-bot/)
[![Mattermost](https://img.shields.io/badge/mattermost-4.0+-blue.svg)](http://www.mattermost.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://pypi.org/project/mmpy-bot/)

Documentation available at [Read the Docs](http://mmpy_bot.readthedocs.org/).


## What is This

A pchat bot for organizing links posted across groups[Mattermost](http://www.mattermost.org).

## Features

* Based on Mattermost [API(V4.0.0)](https://api.mattermost.com)
* Simple plugins mechanism
* Messages can be handled concurrently
* Automatically reconnect to Mattermost when connection is lost
* Python3 Support
* Commands based bot utility
* Commands with their usage visible on bot
* Supports Link aggregation across channels in a team
* Supports Link search with filtering based on time period and hashtags
* Support for subscribing to periodic updates of links (daily/weekly/monthly)
* Support for unsubcribing to periodic link updates
* On bot start, support for auto updates of link aggregation for an already subscribed user
* Support for display Link aggregation results with formatting and markdown



## Compatibility

|    Mattermost    |  mmpy_bot   |
|------------------|:-----------:|
|     >= 4.0       |  > 1.2.0    |
|     <  4.0       | unsupported |


## Installation

```
pip install mmpy_bot
```

## Usage

### Registration

First you need create the mattermost email/password for your bot.

For use all API(V4.0.0), you need add bot user to system admin group to avoid 403 error.

### Configuration

Then you need to configure the `BOT_URL`, `BOT_LOGIN`, `BOT_PASSWORD`, `BOT_TEAM` in a python module
`mmpy_bot_settings.py`, which must be located in a python import path.


mmpy_bot_settings.py:

```python
SSL_VERIFY = True  # Whether to perform SSL cert verification
BOT_URL = 'http://<mm.example.com>/api/v4'  # with 'http://' and with '/api/v4' path. without trailing slash.
BOT_LOGIN = '<bot-email-address>'
BOT_PASSWORD = '<bot-password>'
BOT_TOKEN = None # or '<bot-personal-access-token>' if you have set bot personal access token.
BOT_TEAM = '<your-team>'  # possible in lowercase
WEBHOOK_ID = '<bot-webhook-id>' # otherwise the bot will attempt to create one
```

Alternatively, you can use the environment variable `MATTERMOST_BOT_URL`,
`MATTERMOST_BOT_LOGIN`, `MATTERMOST_BOT_PASSWORD`, `MATTERMOST_BOT_TEAM`,
`MATTERMOST_BOT_SSL_VERIFY`, `MATTERMOST_BOT_TOKEN`

or `MATTERMOST_BOT_SETTINGS_MODULE` environment variable, which provide settings module

```bash
MATTERMOST_BOT_SETTINGS_MODULE=settings.bot_conf mmpy_bot
```


### Run the bot

Use the built-in cli script and point to your custom settings file.

```bash
MATTERMOST_BOT_SETTINGS_MODULE=mmpy_bot_settings mmpy_bot
```

or you can create your own startup file. For example `run.py`:

```python
from mmpy_bot.bot import Bot


if __name__ == "__main__":
    Bot().run()
```

Now you can talk to your bot in your mattermost client!


## Plugins

A chat bot is meaningless unless you can extend/customize it to fit your own use cases.

To write a new plugin, simply create a function decorated by `mmpy_bot.bot.respond_to` or `mmpy_bot.bot.listen_to`:

- A function decorated with `respond_to` is called when a message matching the pattern is sent to the bot (direct message or @botname in a channel/group chat)
- A function decorated with `listen_to` is called when a message matching the pattern is sent on a channel/group chat (not directly sent to the bot)

```python
import re

from mmpy_bot.bot import listen_to
from mmpy_bot.bot import respond_to


@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('I can understand hi or HI!')


@respond_to('I love you')
def love(message):
    message.reply('I love you too!')


@listen_to('Can someone help me?')
def help_me(message):
    # Message is replied to the sender (prefixed with @user)
    message.reply('Yes, I can!')

    # Message is sent on the channel
    # message.send('I can help everybody!')
```

To extract params from the message, you can use regular expression:
```python
from mmpy_bot.bot import respond_to


@respond_to('Give me (.*)')
def give_me(message, something):
    message.reply('Here is %s' % something)
```

If you would like to have a command like 'stats' and 'stats start_date end_date', you can create reg ex like so:

```python
from mmpy_bot.bot import respond_to
import re


@respond_to('stat$', re.IGNORECASE)
@respond_to('stat (.*) (.*)', re.IGNORECASE)
def stats(message, start_date=None, end_date=None):
    pass
```

If you don't want to expose some bot commands to public, you can add `@allowed_users()` or `@allowed_channels()` like so:

```python
@respond_to('^admin$')
@allow_only_direct_message() #only trigger by direct message, remove this line if you want call this in channel
@allowed_users('Your username or email address here','user@email.com') # List of usernames or e-mails allowed
@allowed_channels('allowed_channel_1','allowed_channel_2')  # List of allowed channels
def users_access(message):
    pass
```
Keep in mind the order matters! `@respond_to()` and `@listen_to()`must come before the "allowed" decorators.


And add the plugins module to `PLUGINS` list of mmpy_bot settings, e.g. mmpy_bot_settings.py:

```python
PLUGINS = [
    'mmpy_bot.plugins',
    'devops.plugins',          # e.g. git submodule:  domain:devops-plugins.git
    'programmers.plugins',     # e.g. python package: package_name.plugins
    'frontend.plugins',        # e.g. project tree:   apps.bot.plugins
]
```
*For example you can separate git repositories with plugins on your team.*


If you are migrating from `Slack` to the `Mattermost`, and previously you are used `SlackBot`,
you can use this battery without any problem. On most cases your plugins will be working properly
if you are used standard API or with minimal modifications.