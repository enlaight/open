from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine, Column, Integer, TEXT, DateTime, JSON, TIMESTAMP
from sqlalchemy.dialects.mysql import LONGTEXT
from constants import *

Base = declarative_base()

class YouscanIngestionFiles(Base):
    __tablename__ = 'youscan_ingestion_files'

    id = Column(Integer, primary_key=True)
    uuid = Column(TEXT)
    youscan_topic_id = Column(Integer)
    file_name = Column(TEXT)
    collected_at = Column(DateTime)
    total_collected = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class YouscanTopics(Base):
    __tablename__ = 'youscan_topics'

    id = Column(Integer, primary_key=True)
    uuid = Column(TEXT)
    youscan_topic_id = Column(Integer)
    name = Column(TEXT)
    query = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class YouscanMentions(Base):
    __tablename__ = 'youscan_mentions'

    id = Column(Integer, primary_key=True)
    uuid = Column(TEXT)
    youscan_mention_id = Column(TEXT)
    youscan_topic_id = Column(Integer)
    youscan_added_at = Column(DateTime)
    published_at = Column(DateTime)
    url = Column(TEXT)
    image_url = Column(TEXT)
    title = Column(LONGTEXT)
    text = Column(LONGTEXT)
    full_text = Column(LONGTEXT)
    source = Column(TEXT)
    author = Column(JSON)
    source = Column(TEXT)
    sentiment = Column(TEXT)
    resource_type = Column(TEXT)
    publication_place = Column(JSON)
    language = Column(TEXT)
    country = Column(TEXT)
    city = Column(TEXT)
    region = Column(TEXT)
    post_type = Column(TEXT)
    post_id = Column(TEXT)
    discussion_id = Column(TEXT)
    potential_reach = Column(Integer)
    engagement = Column(JSON)
    tags = Column(JSON)
    auto_categories = Column(JSON)
    subjects = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class YouscanTranslations(Base):
    __tablename__ = 'youscan_translations'

    id = Column(Integer, primary_key=True)
    engine = Column(TEXT)
    uuid = Column(TEXT)
    youscan_mention_id = Column(Integer) # model id, not youscan original id (which is a string)
    field = Column(TEXT)
    source_language = Column(TEXT)
    target_language = Column(TEXT)
    translation = Column(LONGTEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class YouscanClassifications(Base):
    __tablename__ = 'youscan_classifications'

    id = Column(Integer, primary_key=True)
    uuid = Column(TEXT)
    youscan_translation_id = Column(Integer)
    classification_type = Column(TEXT)
    classification_subtype = Column(TEXT)
    version = Column(TEXT)
    engine = Column(TEXT)
    field = Column(TEXT)
    result = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class YouscanPostprocessResults(Base):
    __tablename__ = 'youscan_post_process_results'

    id = Column(Integer, primary_key=True)
    uuid = Column(TEXT)
    source_id = Column(Integer)
    source_type = Column(TEXT)
    process_type = Column(TEXT)
    process_subtype = Column(TEXT)
    version = Column(TEXT)
    field = Column(TEXT)
    result = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


# Declare and create the database connection engine
engine = create_engine(DATABASE_URL)
