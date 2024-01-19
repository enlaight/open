# Global constants
TOPICS_TO_SCAN = [
    344321,
    344331,
    344322,
]

import sys
sys.path.append('.')
sys.path.append('..')
from constants import *
import os
from datetime import datetime, time, timedelta
import requests
import json
import uuid
import traceback

from common import upload_json_to_azure, log_error


# Parse topic list from the youscan API
def get_topics():
    url_method = f'{YOUSCAN_URL}topics/?apiKey={YOUSCAN_API_KEY}'

    response = requests.get(url_method)
    response.raise_for_status()

    json_response = response.json()

    topics = json_response['topics']
    topic_dict = {}
    for topic in topics:
        topic_dict[topic['id']] = {}
        topic_dict[topic['id']]['name'] = topic['name']
        topic_dict[topic['id']]['query'] = topic['query']

    return topic_dict

# Parse mentions from the youscan API
def get_mentions(topic_id, dt_from, dt_to, since_seq='', size='1000'):
    # A coleta DEVE sempre respeitar a ordem que as menções foram salvas no tópico. Dessa forma garantimos a coleta incremental seguindo a ordem cronológica dos eventos.
    order_by = 'seqAsc'

    # URL
    url_method = f'{YOUSCAN_URL}topics/{topic_id}/mentions/?apiKey={YOUSCAN_API_KEY}&from={dt_from}&to={dt_to}&sinceSeq={since_seq}&size={size}&orderBy={order_by}'

    response = requests.get(url_method)

    # Check the response status code
    if response.status_code == 200:
        
        # Request successful
        data = response.json()

        # Process the response data as needed
        total = data['total']
        last_seq = data['lastSeq']

        return data
    
    else:
        # Request failed
        print(f'Request failed with status code: {response.status_code}')
        print(response.text)
        return False


# Actual task to be completed starts here

# Retrienve initial list of topics
topic_dict = get_topics()

# Now iterate over the list of topics and collect the mentions for each one
for topic_id in TOPICS_TO_SCAN:
    try:
        # Find current topic in the topics dictionary
        current_topic = topic_dict[topic_id]

        # Now prepare and perform the actual request for mentions
        url_method = f'{YOUSCAN_URL}topics/{topic_id}/history?apiKey={YOUSCAN_API_KEY}'
        session = requests.Session()
        response = session.get(url=url_method)
        response.raise_for_status()
        json_response = response.json()

        # Initialize date limit params, since this task is run periodically, we can simply get the mentions from the last 24 hours
        # starting from the last midnight (i.e. we get data from the last full day)
        current_datetime = datetime.now()
        last_midnight = datetime.combine(datetime.today(), time.min)
        previous_midnight = last_midnight - timedelta(days=1)
        start_date = previous_midnight.strftime("%Y-%m-%d")
        end_date = last_midnight.strftime("%Y-%m-%d")

        # Initialize variables needed for pagination
        since_seq = ''
        size = 1000
        number_of_mentions = 0
        keep_colleting = True
        combined_mentions = []

        # Keep collecting mentions until we reach the end of the list
        while keep_colleting:
            mentions = get_mentions(
                topic_id=topic_id,
                dt_from=start_date,
                dt_to=end_date,
                since_seq=since_seq,
                size=size
            )

            # Check if we got a valid response, otheriwse raise an exception and simpyl exit the script
            if not mentions:
                raise Exception('Error while collecting mentions')

            # Append the current batch of mentions to the list of all mentions for the current topic
            combined_mentions = combined_mentions + mentions['mentions']

            # Check if we reached the end of the list and should stop requesting new batches
            number_of_mentions = len(mentions['mentions'])
            if number_of_mentions < size or number_of_mentions == 0:
                keep_colleting = False
            else:
                # Update pagination with seq_id of the last mention in the current batch
                since_seq = combined_mentions[-1]['seq']
        
        # Prepare data for export
        unique_identifier = uuid.uuid4().hex # randon string to uniquely identify this entry

        mentions_dict = {}
        mentions_dict['topic_id'] = topic_id
        mentions_dict['uuid'] = unique_identifier
        mentions_dict['collection_datetime'] = current_datetime.isoformat()
        mentions_dict['total'] = len(combined_mentions)
        mentions_dict['topic'] = current_topic
        mentions_dict['mentions'] = combined_mentions

        # Filename of the exported file with the dump of the mentions
        file_name = f'youscan_mentions_{topic_id}_{start_date}_{unique_identifier}.json'
        folder_name = 'raw/'

        # Upload the file to the data lake
        upload_json_to_azure(mentions_dict, folder_name + file_name, DATALAKE_YOUSCAN_ACCOUNT_CONTAINER, DATALAKE_CONNECTION_STRING)

    # Log any errors that might have happened
    except Exception as e:
        log_error(traceback.format_exc(), __file__)
