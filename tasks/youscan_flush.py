import sys
sys.path.append('.')
sys.path.append('..')
from constants import *
from models import *
from common import move_file_in_azure_container, list_files_in_azure_container, log_error
from sqlalchemy import select
from sqlalchemy.orm import Session
import requests, uuid, json
from dateutil import parser
import traceback
from datetime import datetime

# Get the list of files in the raw folder from the Azure storage container
files = list_files_in_azure_container(DATALAKE_YOUSCAN_ACCOUNT_CONTAINER, DATALAKE_CONNECTION_STRING, folder_path = 'raw/')
for file in files:
    try:
        # Get file name without path, we will use it to create the destination path and insert it into the database
        file_name = file.name.split('/')[-1]

        # Retrieve the file from the Azure storage container and load it as a JSON object
        url = file.url
        response = requests.get(file.url, allow_redirects=True)
        mentions_dict = json.loads(response.content)

        # Flush file metadata to the database
        with Session(engine) as session:
            # Check if the file has already been ingested into the database by looking for the UUID
            query = select(YouscanIngestionFiles).where(YouscanIngestionFiles.uuid == mentions_dict['uuid'])
            
            # If the file has already been ingested, skip it
            if session.scalars(query).first() is None:
                with Session(engine) as session:
                    # Create a file entry if it doesn't exist
                    file_db_entry = YouscanIngestionFiles(
                        uuid=mentions_dict['uuid'],
                        youscan_topic_id=mentions_dict['topic_id'],
                        file_name=file_name,
                        collected_at=parser.parse(mentions_dict['collection_datetime']),
                        total_collected=mentions_dict['total']
                    )
                    session.add(file_db_entry)
                    session.commit()
        
                # Flush topic data to the database
                with Session(engine) as session:
                    # Check if the topic has already been ingested into the database by looking for the Youscan topic ID
                    query = select(YouscanTopics).where(YouscanTopics.youscan_topic_id == mentions_dict['topic_id'])

                    # If the topic has already been ingested, skip it
                    if session.scalars(query).first() is None:
                        with Session(engine) as session:
                            # Create a topic entry if it doesn't exist
                            topic_db_entry = YouscanTopics(
                                uuid=uuid.uuid4().hex,
                                youscan_topic_id=mentions_dict['topic_id'],
                                name=mentions_dict['topic']['name'],
                                query=mentions_dict['topic']['query']
                            )
                            session.add(topic_db_entry)
                            session.commit()

                # Flush mentions data to the database
                for mention in mentions_dict['mentions']:
                    with Session(engine) as session:
                        # Check if the mention has already been ingested into the database by looking for the Youscan ID
                        query = select(YouscanMentions).where(YouscanMentions.youscan_mention_id == mention['id'])

                        # If the mention has already been ingested, skip it
                        if session.scalars(query).first() is None:
                            with Session(engine) as session:
                                # Create a mention entry if it doesn't exist
                                mention_db_entry = YouscanMentions(
                                    uuid=uuid.uuid4().hex,
                                    youscan_mention_id=mention['id'],
                                    youscan_topic_id=mentions_dict['topic_id'],
                                    youscan_added_at=parser.parse(mention['addedAt']),
                                    published_at=parser.parse(mention['published']),
                                    url=mention['url'] if 'url' in mention else None,
                                    image_url=mention['imageUrl'] if 'imageUrl' in mention else None,
                                    title=mention['title'] if 'title' in mention else None,
                                    text=mention['text'] if 'text' in mention else None,
                                    full_text=mention['fullText'] if 'fullText' in mention else None,
                                    source=mention['source'].replace('"', '') if 'source' in mention else None,
                                    author=mention['author'] if 'author' in mention else None,
                                    sentiment=mention['sentiment'] if 'sentiment' in mention else None,
                                    resource_type=mention['resourceType'] if 'resourceType' in mention else None,
                                    publication_place=mention['publicationPlace'] if 'publicationPlace' in mention else None,
                                    language=mention['language'] if 'language' in mention else None,
                                    country=mention['country'] if 'country' in mention else None,
                                    city=mention['city'] if 'city' in mention else None,
                                    region=mention['region'] if 'region' in mention else None,
                                    post_type=mention['postType'] if 'postType' in mention else None,
                                    post_id=mention['postId'] if 'postId' in mention else None,
                                    discussion_id=mention['discussionId'] if 'discussionId' in mention else None,
                                    potential_reach=mention['potentialReach'] if 'potentialReach' in mention else None,
                                    engagement=mention['engagement'] if 'engagement' in mention else None,
                                    tags=mention['tags'] if 'tags' in mention else None,
                                    auto_categories=mention['autoCategories'] if 'autoCategories' in mention else None,
                                    subjects=mention['subjects'] if 'subjects' in mention else None
                                )
                                session.add(mention_db_entry)
                                session.commit()
        
        # Move file to the ingested folder once we are done with it
        if not DRY_RUN_MOVE_FILES_ALONG_PIPELINE:
            move_file_in_azure_container(DATALAKE_YOUSCAN_ACCOUNT_CONTAINER, DATALAKE_CONNECTION_STRING, file.name, 'ingested/' + file_name)
    
    # Log any errors that might have happened
    except Exception as e:
        if RUN_AS_DAG:
            log_error(traceback.format_exc(), __file__)
        else:
            raise e
