from __future__ import print_function

from datetime import datetime, timedelta
import json
import os
import xml.etree.ElementTree as ET

import requests

# <stop tag="7353" title="3rd St &amp; Marin St" lat="37.7489999" lon="-122.38744" stopId="17353"/>
MUNI_API_URL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=sf-muni&r=KT&stopId=17353'


def get_predictions():
    """Fetch and return a list of predictions"""
    try:
        response = requests.get(MUNI_API_URL)
        xml_root = ET.fromstring(response.text)
        return list(prediction.attrib for prediction in xml_root[0][0])
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


if __name__ == '__main__':
    post_slack(get_predictions())
