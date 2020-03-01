# -*- coding: utf-8 -*-
import logging
import re
import time
import link_constants
from linkbot import session, settings
from linkbot.bot import listen_to, respond_to
from linkbot.scheduler import schedule, catch_exceptions
from linkbot.utils import allow_only_direct_message
from linkbot.bot_constants import SCHEDULED_UPDATE_TIME_INTERVAL
from linkbot.plugins.link_models import Link, Tag, BotSubscriber
from linkbot.plugins.link_utils import populate_params, message_response, populate_link_data, pretty_print, pretty_print_table

logger = logging.getLogger(__name__)


@respond_to('^test$', re.IGNORECASE)
def test_listen(message):
    message.reply("Hello %s! Test successful" % message.get_username())


@respond_to('^testdb$$', re.IGNORECASE)
@allow_only_direct_message()
def test_db(message):
    link_table = session.query(Link).all()
    message.reply('**Printing Link Table - **\n%s' % pretty_print_table(link_table))
    tag_table = session.query(Tag).all()
    message.reply('**Printing Tag Table - **\n%s' % pretty_print_table(tag_table))
    bot_subscriber_table = session.query(BotSubscriber).all()
    message.reply('**Printing BotSubscriber Table - **\n%s' % pretty_print_table(bot_subscriber_table))


@listen_to('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def link_listen(message):
    # get relevant info from message 
    author = message._get_sender_name()
    channel = message.get_channel_name()
    message_text = message.get_message()
    logger.info('Params: Author = %s, channel = %s, Message = %s' % (author, channel, message_text))

    # extract link from message
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)[0]
    ts = str(time.time())

    tags = [i[1:]  for i in message_text.split() if i.startswith("#") ]

    # clean message
    message_text = message_text.replace(url, "")

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


@respond_to('^links .*$')
@catch_exceptions(cancel_on_failure=True)
def get_aggregated_links(message, userId=None, teamId=None, channelId=None):
    days, tags, channels = populate_params(message, userId, teamId)
    result = populate_link_data(days, tags, channels, message)
    if result == []:
        if message.get_message() == 'subscribe':
            message.reply('There have been no posts for the past 7 days :| Please wait for the next update!')
        else:
            message.reply("Unable to find Links matching your criteria :| Please try changing your search criteria!")
    else:
        scheduled_update = True
        if message._body:
            scheduled_update = False
        message_response(message, pretty_print(result, scheduled_update), channelId)
    logger.info("Bot Log : Function=get_aggregated_links() - aggregated link updates based on filter criteria")


@respond_to('^subscribe$', re.IGNORECASE)
@allow_only_direct_message()
def subscribe_links_summary(message):
    '''
    Subscribes sender of message of Link aggregation scheduled update by the bot
    Currently Link aggregation update is scheduled for every 30 seconds for testing purposes
     - schedule.every(SCHEDULED_UPDATE_TIME_INTERVAL).seconds.do(get_aggregated_links, message).tag(userId)

    For production, Link aggregation update can be scheduled every day at 10:00 AM by setting
     - schedule.every().day().at("10:00").do(get_aggregated_links, message).tag(userId)

    This functionality can be extended to support periodic scheduling for daily/weekly/monthly time period.

    Above changes also need to be reflected in 'run_scheduled_update_jobs()' function in 'bot.bot' module
    '''
    userId = message.get_user_id()

    alreadyBotSubscribed = session.query(BotSubscriber).filter(BotSubscriber.user_id == userId).all()

    if alreadyBotSubscribed != []:
        message.reply("You are already a subscriber of the my updates! :) Wait for the next update!")
        return

    # scheduled link aggregation
    schedule.every(SCHEDULED_UPDATE_TIME_INTERVAL).seconds.do(get_aggregated_links, message).tag(userId)

    botSubcriber = BotSubscriber(user_id=userId, team_id=message.get_teams_of_user(userId)[0][u'id'], \
                                 channel_id=message.channel)
    session.add(botSubcriber)
    session.flush()
    session.commit()
    message.reply("Successfully subscribed for my updates! Wait for the next update! :)")
    logger.info("Bot Log : Function=subscribe_links_summary() - user subscribed from scheduled link updates")


@respond_to('^unsubscribe$', re.IGNORECASE)
@allow_only_direct_message()
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
    message.reply("You have been successfully unsubscribed! :)")
    logger.info("Bot Log : Function=unsubscribe_links_summary() - user unsubscribed from scheduled link updates")


test_listen.__doc__ = link_constants.TEST_LISTEN_DOC
test_db.__doc__ = link_constants.TEST_DB_DOC
link_listen.__doc__ = link_constants.LINK_LISTEN_DOC
get_aggregated_links.__doc__ = link_constants.LINK_AGGREGATION_DOC
subscribe_links_summary.__doc__ = link_constants.LINK_SUBSCRIBE_DOC
unsubscribe_links_summary.__doc__ = link_constants.LINK_UNSUBSCRIBE_DOC
