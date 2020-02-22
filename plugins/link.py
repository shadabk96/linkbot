# -*- coding: utf-8 -*-

import re
import time

from mmpy_bot.bot import listen_to
from mmpy_bot.bot import respond_to
from mmpy_bot.plugins.models import Link
from mmpy_bot import session

@listen_to('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def link_listen(message):
    # get relevant info from message 
    author = message._get_sender_name()
    channel = message.get_channel_name()
    message_text = message.get_message()
    print "author " + author
    print "channel " + channel
    print "message_text " + message_text
    print message
    message.reply('link reached')

    # extract link from message
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)[0]
    print url
    ts = str(time.time())

    # store in db
    link = Link(author = author, message = message_text, link = url, channel = channel, timestamp = ts)
    session.add(link)
    session.commit()

    result = session.query(Link).filter(Link.author.in_(['@shadab'])).first()
    message.reply(result)
    print result

@listen_to('test')
def test_listen(message):
    message.reply("test reached 1")
    message.reply("test reached 2")
