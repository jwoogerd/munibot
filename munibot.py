from __future__ import print_function

from datetime import datetime, timedelta
import json
import math
import os
import time
import xml.etree.ElementTree as ET

import requests

import config


# <stop tag="7353" title="3rd St &amp; Marin St" lat="37.7489999" lon="-122.38744" stopId="17353"/>
MUNI_API_URL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=sf-muni&r=KT&stopId=17353'


def get_predictions():
    """Fetch and return a list of predictions"""
    try:
        response = requests.get(MUNI_API_URL)
        xml_root = ET.fromstring(response.text)
        # body (XML root) -> predictions -> direction contains predictions
        # for the next few trains.
        predictions = list(prediction.attrib for prediction in xml_root[0][0])
        # Only include predictions for trains coming in >= the lookahead time. These
        # are the trains that we can reasonably expect to catch.
        relevant_predictions = filter(
            lambda p: int(p.get('minutes')) >= config.LOOKAHEAD_MINS, predictions)
        # Return the relevant predictions sorted in ascending order by the minutes til
        # arrival.
        return sorted(relevant_predictions,
                      lambda p1, p2: int(p1.get('minutes')) - int(p2.get('minutes')))
    except requests.exceptions.ConnectionError:
        print('Unable to fetch muni data')


def post_slack(predictions):
    slack_webhook = os.environ.get('SLACK_HOOK')
    now = datetime.now()
    formatted_strings = []

    for p in predictions:
        minutes = p.get('minutes')
        departure_time = (now + timedelta(minutes=int(minutes))).strftime('%I:%M%p')
        s = '%s %s  --  departs at %s (in %s minutes)' % (u'\U0001F683', p.get('vehicle'), departure_time, minutes)
        formatted_strings.append(s)

    pretext = '*Muni schedule for KT Outbound 3rd & Marin Street*'
    fields = [{
        'title': 'Upcoming trains',
        'value': '\n'.join(formatted_strings),
        'short': False,
    }]
    payload = {
        'text': pretext,
        'mrkdwn': True,
        'attachments': [{
            'fallback': pretext,
            'color': '#1f479e',
            'fields': fields,
        }]
    }
    requests.post(slack_webhook, data=json.dumps(payload))


def bot_should_be_active(dt):
    return (dt.weekday() in config.ACTIVE_WEEKDAYS
            and dt.hour >= config.START_HOUR
            and dt.hour < config.END_HOUR)


"""
Given a datetime, determines the number of seconds until the immediate next time
that the bot should be active. From the config, we know the hour for which we should
start the bot. All we have to determine is the next date for which the bot should be active (call this til_day).

The til_day could be the current weekday, if we haven't passed the end hour of
activity for the day yet. Otherwise, the til_day would at best be the following day.
If the following day is not a day for which the bot should be active, then try to
find the first active weekday following til_day. Note, this could be the first
active weekday of the following week.

Once we have determined the next date and time that the bot should be active, simply
determine the total seconds between these two datetimes.
"""
def secs_til_active(dt):
    til_day = dt.weekday()
    if dt.hour >= config.END_HOUR:
        til_day = (til_day + 1) % 7
    if til_day not in config.ACTIVE_WEEKDAYS:
        future_days_this_wk = sorted(
            filter(lambda d: d > til_day, config.ACTIVE_WEEKDAYS))
        if future_days_this_wk:
            til_day = future_days_this_wk[0]
        else:
            til_day = sorted(config.ACTIVE_WEEKDAYS)[0]
    # Determine how many days ahead of the input dt til_day is, and
    # create a datetime object with this future date.
    dt_ahead = dt + timedelta(days=(til_day - dt.weekday()) % 7)
    # Find timedelta in seconds between dt_ahead at starting hour and
    # the input datetime, dt.
    return math.floor((datetime(
        dt_ahead.year, dt_ahead.month, dt_ahead.day,
        config.START_HOUR, 0, 0, 0) - dt).total_seconds()
    )


if __name__ == '__main__':
    while True:
        dt = datetime.now()
        if bot_should_be_active(dt):
            print("Requesting Muni train schedule at %s" %
                  dt.strftime('%Y-%m-%d %H:%M:%S'))
            predictions = get_predictions()
            if predictions:
                upcoming_pred = predictions[0]
                if int(upcoming_pred.get('minutes')) == config.LOOKAHEAD_MINS:
                    post_slack(predictions)
                    print("Posted predictions to slack.")
            time.sleep(60)  # When active, pull from API once every minute.
        else:
            print("Outside active times, sleeping for %ds..." % secs_til_active(dt))
            time.sleep(secs_til_active(dt))
