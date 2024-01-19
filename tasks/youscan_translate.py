import sys
sys.path.append('.')
sys.path.append('..')
import requests, uuid, json
from common import list_files_in_azure_container, log_error
from bs4 import BeautifulSoup
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from common import translate
from constants import *
from models import *

# Create a DB connection session
with Session(engine) as session:
    # filter the metions that do not have a translation attached yet
    sql_query = text('''
        select m.id
        from youscan_translations t
        right join youscan_mentions m
        on m.id = t.youscan_mention_id
        where t.id is null
        and m.full_text is not null;
    ''')
    result = session.execute(sql_query)
    ids_in_need_for_translation = [row[0] for row in result]
    query = select(YouscanMentions).where(YouscanMentions.id.in_(ids_in_need_for_translation))
    for mention in session.scalars(query):
        mention_full_text = BeautifulSoup(mention.full_text, "lxml").text
        mention_translation = translate('ru', 'en', mention_full_text)

        # Create a translation entry in the database
        topic_db_entry = YouscanTranslations(
            uuid=uuid.uuid4().hex,
            engine='azure',
            youscan_mention_id=mention.id,
            field='full_text',
            source_language='ru',
            target_language='en',
            translation=mention_translation,
        )
        session.add(topic_db_entry)
        session.commit()
