"""empty message

Revision ID: 7248fc48ab85
Revises: 
Create Date: 2019-04-23 17:42:42.550080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7248fc48ab85'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog',
    sa.Column('blog_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('like', sa.Integer(), nullable=True),
    sa.Column('sticky', sa.Boolean(), nullable=True),
    sa.Column('category', sa.String(length=200), nullable=True),
    sa.Column('comment_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('blog_id')
    )
    op.create_table('general_settings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('init', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('author', sa.String(length=500), nullable=False),
    sa.Column('post_count', sa.Integer(), nullable=True),
    sa.Column('excerpt', sa.Boolean(), nullable=True),
    sa.Column('comments', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sidebar_settings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('main_position', sa.Integer(), nullable=False),
    sa.Column('post_position', sa.Integer(), nullable=False),
    sa.Column('show_blog_name', sa.Boolean(), nullable=True),
    sa.Column('show_logo', sa.Boolean(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('search', sa.Boolean(), nullable=True),
    sa.Column('recent_posts', sa.Boolean(), nullable=True),
    sa.Column('max_recent', sa.Integer(), nullable=True),
    sa.Column('popular_posts', sa.Boolean(), nullable=True),
    sa.Column('max_popular', sa.Integer(), nullable=True),
    sa.Column('category', sa.Boolean(), nullable=True),
    sa.Column('max_category', sa.Integer(), nullable=True),
    sa.Column('tag', sa.Boolean(), nullable=True),
    sa.Column('max_tag', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('tag_id')
    )
    op.create_table('theme',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('selected', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('bg_color', sa.String(length=10), nullable=False),
    sa.Column('text_color', sa.String(length=10), nullable=False),
    sa.Column('post_container_color', sa.String(length=10), nullable=False),
    sa.Column('blog_name_color', sa.String(length=10), nullable=False),
    sa.Column('header_color', sa.String(length=10), nullable=False),
    sa.Column('alt_header_color', sa.String(length=10), nullable=False),
    sa.Column('link_color', sa.String(length=10), nullable=False),
    sa.Column('like_color', sa.String(length=10), nullable=False),
    sa.Column('comment_color', sa.String(length=10), nullable=False),
    sa.Column('sticky_color', sa.String(length=10), nullable=False),
    sa.Column('main_font', sa.String(length=200), nullable=False),
    sa.Column('header_font', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['blog.blog_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('blog_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blog_id'], ['blog.blog_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags')
    op.drop_table('comment')
    op.drop_table('user')
    op.drop_table('theme')
    op.drop_table('tag')
    op.drop_table('sidebar_settings')
    op.drop_table('general_settings')
    op.drop_table('blog')
    # ### end Alembic commands ###
