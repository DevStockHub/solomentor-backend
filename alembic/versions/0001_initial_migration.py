"""Initial migration

Revision ID: 0001_initial_migration
Revises: 
Create Date: 2026-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mentor_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('subjects', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentor_profiles_id'), 'mentor_profiles', ['id'], unique=False)

    op.create_table(
        'subjects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_subjects_id'), 'subjects', ['id'], unique=False)

    op.create_table(
        'students',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('mentor_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('school', sa.String(length=255), nullable=True),
        sa.Column('grade', sa.String(length=50), nullable=True),
        sa.Column('contact', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['mentor_id'], ['mentor_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)

    op.create_table(
        'student_subjects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_subjects_id'), 'student_subjects', ['id'], unique=False)

    op.create_table(
        'session_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('planned_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_plans_id'), 'session_plans', ['id'], unique=False)

    op.create_table(
        'topics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_plan_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('planned_minutes', sa.Integer(), nullable=False),
        sa.Column('actual_minutes', sa.Integer(), nullable=True),
        sa.Column('extra_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_plan_id'], ['session_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_id'), 'topics', ['id'], unique=False)

    op.create_table(
        'session_notes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_plan_id', sa.String(length=36), nullable=False),
        sa.Column('topic_id', sa.String(length=36), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('approach_used', sa.String(length=255), nullable=True),
        sa.Column('student_struggle', sa.Text(), nullable=True),
        sa.Column('effectiveness_rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_plan_id'], ['session_plans.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_notes_id'), 'session_notes', ['id'], unique=False)

    op.create_table(
        'progress_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=36), nullable=False),
        sa.Column('topic_id', sa.String(length=36), nullable=True),
        sa.Column('session_plan_id', sa.String(length=36), nullable=True),
        sa.Column('approach_used', sa.String(length=255), nullable=True),
        sa.Column('struggle_noted', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(length=255), nullable=True),
        sa.Column('effectiveness_rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_plan_id'], ['session_plans.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progress_records_id'), 'progress_records', ['id'], unique=False)

    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_plan_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('context_snapshot', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_plan_id'], ['session_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_progress_records_id'), table_name='progress_records')
    op.drop_table('progress_records')
    op.drop_index(op.f('ix_session_notes_id'), table_name='session_notes')
    op.drop_table('session_notes')
    op.drop_index(op.f('ix_topics_id'), table_name='topics')
    op.drop_table('topics')
    op.drop_index(op.f('ix_session_plans_id'), table_name='session_plans')
    op.drop_table('session_plans')
    op.drop_index(op.f('ix_student_subjects_id'), table_name='student_subjects')
    op.drop_table('student_subjects')
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_table('students')
    op.drop_index(op.f('ix_subjects_id'), table_name='subjects')
    op.drop_table('subjects')
    op.drop_index(op.f('ix_mentor_profiles_id'), table_name='mentor_profiles')
    op.drop_table('mentor_profiles')
