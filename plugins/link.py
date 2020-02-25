# -*- coding: utf-8 -*-

import re
import time

from mmpy_bot.bot import listen_to
from mmpy_bot.bot import respond_to
from mmpy_bot.plugins.models import Link, Tag
from mmpy_bot import session

@listen_to('^test$', re.IGNORECASE)
def test_listen(message):
    message.reply("test reached 1")
    message.reply("test reached 2")

@listen_to('^testdb$',re.IGNORECASE)
def test_db(message):
    link_table = session.query(Link).all()
    message.reply('Printing Link Table --->\n%s' % pretty_print(link_table))

    tag_table = session.query(Tag).all()
    message.reply('Printing Tag Table --->\n%s' % pretty_print(tag_table))

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


    # extract tags from message
    # tt = re.findall('tags\s*=\s*\[.*\]', message_text)
    # tags = []
    tags = [i[1:]  for i in message_text.split() if i.startswith("#") ]
    print tags

    # store in db
    link = Link(author = author, message = message_text, link = url, channel = channel, timestamp = ts)
    session.add(link)
    session.flush()
    if len(tags) != 0:
        tags_arr = []
        for tag in tags:
            tags_arr.append(Tag(message_id = link.id, tag = tag))
        session.add_all(tags_arr)
    session.commit()

    test_db(message)

@listen_to('^links .*$')
@respond_to('^links .*$')
def get_aggregated_links(message):
    days = int(re.search('^links --days ([1-9])(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[0])
    print days
    message.reply('User has asked aggregated link data for %s days' % days)

    tags = re.search('^links --days ([1-9])(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[3]
    print tags

    user_id = message.get_user_id()
    '''
    Finding the team_id is still pending. Find and replace your local team_id instead of the 
    second parameter in the get_channels_for_user() below
    '''
    channels = message.get_channels_for_user(user_id, '9gf4wftn13rzbc75ojq37hj95o')
    channels = list(map(lambda x: x['name'].encode(), channels))

    from_time = str(time.time() - days*86400.00)

    if tags == None:
        result = session.query(Link).filter(Link.channel.in_(channels), Link.timestamp>=from_time).all()
    else:
        tags = tags.split()
        result = session.query(Link, Tag).filter(Link.id == Tag.message_id, Link.timestamp>=from_time, \
                                                 Link.channel.in_(channels),  Tag.tag.in_(tags)).all()
    message.reply(pretty_print(result))

def pretty_print(result):
    return "\n".join(map(str, result))