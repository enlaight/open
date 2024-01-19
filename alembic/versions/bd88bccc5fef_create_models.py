"""Create models

Revision ID: bd88bccc5fef
Revises: 
Create Date: 2023-08-13 21:52:03.790242

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bd88bccc5fef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('youscan_classifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.TEXT(), nullable=True),
    sa.Column('youscan_translation_id', sa.Integer(), nullable=True),
    sa.Column('classification_type', sa.TEXT(), nullable=True),
    sa.Column('classification_subtype', sa.TEXT(), nullable=True),
    sa.Column('version', sa.TEXT(), nullable=True),
    sa.Column('engine', sa.TEXT(), nullable=True),
    sa.Column('field', sa.TEXT(), nullable=True),
    sa.Column('result', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youscan_ingestion_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.TEXT(), nullable=True),
    sa.Column('youscan_topic_id', sa.Integer(), nullable=True),
    sa.Column('file_name', sa.TEXT(), nullable=True),
    sa.Column('collected_at', sa.DateTime(), nullable=True),
    sa.Column('total_collected', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youscan_mentions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.TEXT(), nullable=True),
    sa.Column('youscan_mention_id', sa.TEXT(), nullable=True),
    sa.Column('youscan_topic_id', sa.Integer(), nullable=True),
    sa.Column('youscan_added_at', sa.DateTime(), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('url', sa.TEXT(), nullable=True),
    sa.Column('image_url', sa.TEXT(), nullable=True),
    sa.Column('title', mysql.LONGTEXT(), nullable=True),
    sa.Column('text', mysql.LONGTEXT(), nullable=True),
    sa.Column('full_text', mysql.LONGTEXT(), nullable=True),
    sa.Column('source', sa.TEXT(), nullable=True),
    sa.Column('author', sa.JSON(), nullable=True),
    sa.Column('sentiment', sa.TEXT(), nullable=True),
    sa.Column('resource_type', sa.TEXT(), nullable=True),
    sa.Column('publication_place', sa.JSON(), nullable=True),
    sa.Column('language', sa.TEXT(), nullable=True),
    sa.Column('country', sa.TEXT(), nullable=True),
    sa.Column('city', sa.TEXT(), nullable=True),
    sa.Column('region', sa.TEXT(), nullable=True),
    sa.Column('post_type', sa.TEXT(), nullable=True),
    sa.Column('post_id', sa.TEXT(), nullable=True),
    sa.Column('discussion_id', sa.TEXT(), nullable=True),
    sa.Column('potential_reach', sa.Integer(), nullable=True),
    sa.Column('engagement', sa.JSON(), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('auto_categories', sa.JSON(), nullable=True),
    sa.Column('subjects', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youscan_topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.TEXT(), nullable=True),
    sa.Column('youscan_topic_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('query', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youscan_translations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('engine', sa.TEXT(), nullable=True),
    sa.Column('uuid', sa.TEXT(), nullable=True),
    sa.Column('youscan_mention_id', sa.Integer(), nullable=True),
    sa.Column('field', sa.TEXT(), nullable=True),
    sa.Column('source_language', sa.TEXT(), nullable=True),
    sa.Column('target_language', sa.TEXT(), nullable=True),
    sa.Column('translation', mysql.LONGTEXT(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('youscan_translations')
    op.drop_table('youscan_topics')
    op.drop_table('youscan_mentions')
    op.drop_table('youscan_ingestion_files')
    op.drop_table('youscan_classifications')
    # ### end Alembic commands ###
