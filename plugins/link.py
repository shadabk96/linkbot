# -*- coding: utf-8 -*-
import logging
import re
import time
from mmpy_bot import session, settings
from mmpy_bot.bot import listen_to, respond_to
from mmpy_bot.plugins.models import Link, Tag, BotSubscriber
from mmpy_bot.scheduler import schedule
from mmpy_bot.bot_constants import SCHEDULED_UPDATE_TIME_INTERVAL

logging.getLogger('schedule').propagate = False
logger = logging.getLogger(__name__)

@listen_to('^test$', re.IGNORECASE)
@respond_to('^test$', re.IGNORECASE)
def test_listen(message):
    message.reply("test reached 1")
    message.reply("test reached 2")

@listen_to('^testdb$',re.IGNORECASE)
@respond_to('^testdb$$')
def test_db(message):
    link_table = session.query(Link).all()
    message.reply('Printing Link Table --->\n%s' % pretty_print(link_table))
    tag_table = session.query(Tag).all()
    message.reply('Printing Tag Table --->\n%s' % pretty_print(tag_table))
    bot_subscriber_table = session.query(BotSubscriber).all()
    message.reply('Printing BotSubscriber Table --->\n%s' % pretty_print(bot_subscriber_table))

@listen_to('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def link_listen(message):
    # get relevant info from message 
    author = message._get_sender_name()
    channel = message.get_channel_name()
    message_text = message.get_message()
    logger.info('Params: Author = %s, channel = %s, Message = %s' % (author, channel, message_text))

    # extract link from message
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)[0]
    print url
    ts = str(time.time())


    # extract tags from message
    # tt = re.findall('tags\s*=\s*\[.*\]', message_text)
    # tags = []
    tags = [i[1:]  for i in message_text.split() if i.startswith("#") ]

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

@listen_to('^links .*$')
@respond_to('^links .*$')
def get_aggregated_links(message, userId=None, teamId=None, channelId=None):
    days, tags, channels = populate_params(message, userId, teamId)
    result = populate_link_data(days, tags, channels, message)
    if result == []:
        if message.get_message() == 'subscribe':
            message.reply('There have been no posts for the past 7 days :| Please wait for the next update!')
        else:
            message.reply("Unable to find Links matching your criteria :| Please try changing your search criteria!")
        return
    message_response(message, pretty_print(result), channelId)


@listen_to('^subscribe$')
@respond_to('^subscribe$')
def subscribe_links_summary(message):
    userId = message.get_user_id()

    alreadyBotSubscribed = session.query(BotSubscriber).filter(BotSubscriber.user_id == userId).all()

    if alreadyBotSubscribed != []:
        message.reply("You are already a subscriber of the my updates! :) Wait for the next update!")
        return

    # scheduled link aggregation
    schedule.every(SCHEDULED_UPDATE_TIME_INTERVAL).seconds.do(get_aggregated_links, message).tag(userId)

    botSubcriber = BotSubscriber(user_id=userId, team_id=message.get_teams_of_user(userId)[0][u'id'], channel_id=message.channel)
    session.add(botSubcriber)
    session.flush()
    session.commit()
    message.reply("Successfully subscribed for my updates! Wait for the next update! :)")

@listen_to('^unsubscribe$')
@respond_to('^unsubscribe$')
def unsubscribe_links_summary(message):

    jobTag = message.get_user_id()

    alreadyBotSubscribed = session.query(BotSubscriber).filter(BotSubscriber.user_id == jobTag).all()

    if alreadyBotSubscribed == []:
        message.reply("You haven't Subscribed for the my updates! Cannot Unsubscribe you :P")
        return

    # clear job
    schedule.clear(jobTag)

    session.query(BotSubscriber).filter(BotSubscriber.user_id == jobTag).delete()
    session.commit()
    message.reply("You have been successfully unsubscribed!")

def populate_params(message, userId=None, teamId=None):
    days, tags = None, None
    if message._body:
        if 'links' in message.get_message():
            days = re.search('^links (--days ([1-9]))?(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[1]
            print days

            tags = re.search('^links (--days ([1-9]))?(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[4]
            print tags

            userId = message.get_user_info('id')
        elif message.get_message() == 'subscribe':
            userId = message.get_user_info('id', 'me')
            print(userId)
            days = 7
    else:
        days = 7
    '''
    Finding the team_id is still pending. Find and replace your local team_id instead of the 
    second parameter in the get_channels_for_user() below
    '''
    channels = message.get_channels_for_user(userId, teamId or message.get_teams_of_user(userId)[0][u'id'])
    channels = list(map(lambda x: x['name'].encode(), channels))

    logger.info("Aggregation Params: Days = %s, Tags = %r, userId = %s, Channels = %r", days, tags, userId, channels)
    return days, tags, channels

def message_response(message, response, channelId=None):
    if message._body:
        message.reply(response)
    else:
        message.send(response, channelId)

def populate_link_data(days, tags, channels, message):
    if tags and days:
        from_time = str(time.time() - int(days) * 86400.00)
        tags = tags.encode().split()
        result = session.query(Link, Tag).filter(Link.id == Tag.message_id, Link.timestamp>=from_time, \
                                                 Link.channel.in_(channels),  Tag.tag.in_(tags)).all()
    elif days and not tags:
        from_time = str(time.time() - int(days) * 86400.00)
        result = session.query(Link).filter(Link.timestamp>=from_time, Link.channel.in_(channels)).all()
    elif not days and tags:
        tags = tags.encode().split()
        result = session.query(Link, Tag).filter(Link.id == Tag.message_id, \
                                                 Link.channel.in_(channels), Tag.tag.in_(tags)).all()
    return result

def pretty_print(result):
    return "\n".join(map(str, result))