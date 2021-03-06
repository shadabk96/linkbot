import re
import logging
import time
from linkbot import session
from linkbot.plugins.link_models import Link, Tag, BotSubscriber
from linkbot.bot_constants import SCHEDULED_UPDATE_NUMBER_OF_DAYS

logger = logging.getLogger(__name__)


def populate_params(message, userId=None, teamId=None):
    days, tags = None, None
    if message._body:
        if 'links' in message.get_message():
            days = re.search('^links (--days ([1-9]))?(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[1]
            tags = re.search('^links (--days ([1-9]))?(\s*)(--tags ([\w\s]+))?$', message.get_message()).groups()[4]
            userId = message.get_user_info('id')
        elif message.get_message() == 'subscribe':
            userId = message.get_user_info('id', 'me')
            days = SCHEDULED_UPDATE_NUMBER_OF_DAYS
    else:
        days = SCHEDULED_UPDATE_NUMBER_OF_DAYS

    channels = message.get_channels_for_user(userId, teamId or message.get_teams_of_user(userId)[0][u'id'])
    channels = list(map(lambda x: x['name'].encode(), channels))

    logger.info("Aggregation Params: Days = %s, Tags = %r, userId = %s, Channels = %r", days, tags, userId, channels)
    return days, tags, channels


def populate_link_data(days, tags, channels, message):
    if tags and days:
        from_time = str(time.time() - int(days) * 86400.00)
        tags = tags.encode().split()
        result = session.query(Link, Tag).filter(Link.id == Tag.message_id, Link.timestamp >= from_time, \
                                                 Link.channel.in_(channels), Tag.tag.in_(tags)).all()
    elif days and not tags:
        from_time = str(time.time() - int(days) * 86400.00)
        result = session.query(Link).filter(Link.timestamp >= from_time, Link.channel.in_(channels)).all()
    elif not days and tags:
        tags = tags.encode().split()
        result = session.query(Link, Tag).filter(Link.id == Tag.message_id, \
                                                 Link.channel.in_(channels), Tag.tag.in_(tags)).all()
    return result


def message_response(message, response, channelId=None):
    if message._body:
        message.reply(response)
    else:
        message.send(response, channelId)


def pretty_print(result, scheduled_update):
    link, tag, botsubscriber, sqa_collection = find_result_type(result)
    if sqa_collection:
        result_dict = {}
        for link, tag in result:
            if link in result_dict:
                result_dict[link].append('#' + tag.tag.encode())
            else:
                result_dict[link] = ['#' + tag.tag.encode()]

        result_string = '#### Here are the results matching your search criteria - \n'
        for link, tags in result_dict.iteritems():
            result_string += '**Message:** %s\n**Link:** %s\n**Hashtags:** %s\n**Sent by:** %s\n**Sent on:** %s' % (
            link.message, link.link, ' '.join(map(str, tags)), link.author,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(link.timestamp))))
            result_string += '\n                                             \n'
        return result_string
    else:
        if scheduled_update:
            result_string = '#### Here is your scheduled Link update - \n'
        else:
            result_string = '#### Here are the results matching your search criteria - \n'
        for link in result:
            result_string += '**Message:** %s\n**Link:** %s\n**Sent by:** %s\n**Sent on:** %s' % (
            link.message, link.link, link.author,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(link.timestamp))))
            result_string += '\n                                             \n'

    return result_string


def pretty_print_table(result):
    return "\n".join(map(str, result))


def find_result_type(result):
    link, tag, botsubscriber, sqa_collection = False, False, False, False
    if isinstance(result[0], Link):
        link = True
    elif isinstance(result[0], Tag):
        tag = True
    elif isinstance(result[0], BotSubscriber):
        botsubscriber = True
    else:
        sqa_collection = True
    return link, tag, botsubscriber, sqa_collection
