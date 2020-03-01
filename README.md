# Linkbot

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

## Setup

* Clone this repository.
* Create a .env file in cloned directory with following lines
```
COFFEEBOT_DATABASE_FILENAME=sqlite.db
```
* Create a new bot account from system console.
* Open settings.py and edit following parameters
```
MATTERMOST_API_VERSION = 4
BOT_URL = 'http://localhost:8065/api/v4'
BOT_TOKEN = ""
BOT_TEAM = ''
SSL_VERIFY = False
```
    * Bot token can be fetched from system console. ([Help](https://docs.mattermost.com/developer/bot-accounts.html))

## Run the bot

* Run the cli.py file by typing `python cli.py`
* Open mattermost instance and send a personal message 'test' to the bot. The bot should reply "Hello" with your username.

