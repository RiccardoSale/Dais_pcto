"""empty message

Revision ID: 10321640f29d
Revises: 
Create Date: 2022-05-31 15:46:10.452995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10321640f29d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('h_schools',
    sa.Column('_hschool_code', sa.String(length=10), nullable=False),
    sa.Column('_name', sa.String(length=64), nullable=False),
    sa.Column('_region', sa.String(length=20), nullable=False),
    sa.Column('_city', sa.String(length=40), nullable=False),
    sa.Column('_street', sa.String(length=64), nullable=False),
    sa.Column('_number', sa.String(length=6), nullable=False),
    sa.Column('_phone', sa.String(length=15), nullable=False),
    sa.PrimaryKeyConstraint('_hschool_code')
    )
    op.create_table('users',
    sa.Column('_user_id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=64), nullable=False),
    sa.Column('_surname', sa.String(length=64), nullable=False),
    sa.Column('_email', sa.String(length=60), nullable=False),
    sa.Column('_password', sa.String(length=128), nullable=False),
    sa.Column('_role', sa.String(length=10), nullable=False),
    sa.Column('_school', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['_school'], ['h_schools._hschool_code'], ),
    sa.PrimaryKeyConstraint('_user_id')
    )
    op.create_index(op.f('ix_users__email'), 'users', ['_email'], unique=True)
    op.create_table('courses',
    sa.Column('_course_id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=64), nullable=False),
    sa.Column('_mode', sa.String(length=10), nullable=False),
    sa.Column('_description', sa.TEXT(), nullable=False),
    sa.Column('_max_student', sa.Integer(), nullable=False),
    sa.Column('_min_student', sa.Integer(), nullable=False),
    sa.Column('_n_hour', sa.Integer(), nullable=False),
    sa.Column('_start_month', sa.DATE(), nullable=False),
    sa.Column('_end_month', sa.DATE(), nullable=False),
    sa.Column('_professor', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['_professor'], ['users._user_id'], ),
    sa.PrimaryKeyConstraint('_course_id')
    )
    op.create_index(op.f('ix_courses__name'), 'courses', ['_name'], unique=True)
    op.create_table('lessons',
    sa.Column('_lesson_id', sa.Integer(), nullable=False),
    sa.Column('_start_hour', sa.TIME(), nullable=False),
    sa.Column('_end_hour', sa.TIME(), nullable=False),
    sa.Column('_date', sa.DATE(), nullable=False),
    sa.Column('_mode', sa.String(length=10), nullable=False),
    sa.Column('_link', sa.String(length=2083), nullable=False),
    sa.Column('_structure', sa.String(length=64), nullable=True),
    sa.Column('_description', sa.TEXT(), nullable=False),
    sa.Column('_secret_token', sa.String(length=32), nullable=False),
    sa.Column('course', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course'], ['courses._course_id'], ),
    sa.PrimaryKeyConstraint('_lesson_id')
    )
    op.create_table('user_corse',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses._course_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users._user_id'], )
    )
    op.create_table('user_lesson',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons._lesson_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users._user_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_lesson')
    op.drop_table('user_corse')
    op.drop_table('lessons')
    op.drop_index(op.f('ix_courses__name'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_users__email'), table_name='users')
    op.drop_table('users')
    op.drop_table('h_schools')
    # ### end Alembic commands ###
