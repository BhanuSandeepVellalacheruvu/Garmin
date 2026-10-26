"""Initial schema for Garmin AI Performance Lab

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_profiles
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('username', sa.String(length=100), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('timezone', sa.String(length=60), nullable=False, server_default='UTC'),
        sa.Column('preferred_units', sa.String(length=10), nullable=False, server_default='metric'),
        sa.Column('experience_level', sa.String(length=30), nullable=False, server_default='intermediate'),
        sa.Column('target_race_distance', sa.String(length=30), nullable=True),
        sa.Column('target_finish_time', sa.Integer(), nullable=True),
        sa.Column('preferred_running_days', sa.JSON(), nullable=True),
        sa.Column('weekly_availability_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # activities
    op.create_table(
        'activities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('garmin_activity_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('sport_type', sa.String(length=60), nullable=False),
        sa.Column('activity_type', sa.String(length=60), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('distance_meters', sa.Float(), nullable=True),
        sa.Column('avg_heart_rate', sa.Integer(), nullable=True),
        sa.Column('max_heart_rate', sa.Integer(), nullable=True),
        sa.Column('avg_speed_ms', sa.Float(), nullable=True),
        sa.Column('max_speed_ms', sa.Float(), nullable=True),
        sa.Column('elevation_gain', sa.Float(), nullable=True),
        sa.Column('elevation_loss', sa.Float(), nullable=True),
        sa.Column('avg_cadence', sa.Integer(), nullable=True),
        sa.Column('calories', sa.Integer(), nullable=True),
        sa.Column('training_effect_aerobic', sa.Float(), nullable=True),
        sa.Column('training_effect_anaerobic', sa.Float(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_activity_user_start', 'activities', ['user_id', 'start_time'])
    op.create_index('ix_activity_sport', 'activities', ['user_id', 'sport_type'])

    # activity_laps
    op.create_table(
        'activity_laps',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('activity_id', sa.String(length=36), sa.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lap_index', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('distance_meters', sa.Float(), nullable=True),
        sa.Column('avg_heart_rate', sa.Integer(), nullable=True),
        sa.Column('avg_speed_ms', sa.Float(), nullable=True),
        sa.Column('avg_cadence', sa.Integer(), nullable=True),
        sa.Column('elevation_gain', sa.Float(), nullable=True),
    )
    op.create_index('ix_lap_activity', 'activity_laps', ['activity_id'])

    # activity_samples
    op.create_table(
        'activity_samples',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('activity_id', sa.String(length=36), sa.ForeignKey('activities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('speed_ms', sa.Float(), nullable=True),
        sa.Column('cadence', sa.Integer(), nullable=True),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
    )
    op.create_index('ix_sample_activity_time', 'activity_samples', ['activity_id', 'timestamp'])

    # daily_health_metrics
    op.create_table(
        'daily_health_metrics',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('calendar_date', sa.Date(), nullable=False),
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('active_minutes', sa.Integer(), nullable=True),
        sa.Column('resting_heart_rate', sa.Integer(), nullable=True),
        sa.Column('avg_stress_level', sa.Integer(), nullable=True),
        sa.Column('body_battery_high', sa.Integer(), nullable=True),
        sa.Column('body_battery_low', sa.Integer(), nullable=True),
        sa.Column('respiration_avg', sa.Float(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'calendar_date', name='uq_health_user_date'),
    )
    op.create_index('ix_health_user_date', 'daily_health_metrics', ['user_id', 'calendar_date'])

    # sleep_records
    op.create_table(
        'sleep_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('calendar_date', sa.Date(), nullable=False),
        sa.Column('sleep_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sleep_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_sleep_seconds', sa.Integer(), nullable=True),
        sa.Column('deep_sleep_seconds', sa.Integer(), nullable=True),
        sa.Column('light_sleep_seconds', sa.Integer(), nullable=True),
        sa.Column('rem_sleep_seconds', sa.Integer(), nullable=True),
        sa.Column('awake_seconds', sa.Integer(), nullable=True),
        sa.Column('sleep_score', sa.Integer(), nullable=True),
        sa.Column('hrv_weekly_avg', sa.Float(), nullable=True),
        sa.Column('hrv_last_night', sa.Float(), nullable=True),
        sa.Column('hrv_last_night_5min_high', sa.Float(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'calendar_date', name='uq_sleep_user_date'),
    )
    op.create_index('ix_sleep_user_date', 'sleep_records', ['user_id', 'calendar_date'])

    # race_goals
    op.create_table(
        'race_goals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('race_name', sa.String(length=255), nullable=False),
        sa.Column('race_date', sa.Date(), nullable=True),
        sa.Column('distance_meters', sa.Float(), nullable=True),
        sa.Column('target_time_seconds', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # personal_records
    op.create_table(
        'personal_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity_id', sa.String(length=36), sa.ForeignKey('activities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('record_type', sa.String(length=60), nullable=False),
        sa.Column('distance_meters', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('achieved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # training_plans
    op.create_table(
        'training_plans',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('race_goal_id', sa.String(length=36), sa.ForeignKey('race_goals.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_by', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # training_plan_days
    op.create_table(
        'training_plan_days',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('plan_id', sa.String(length=36), sa.ForeignKey('training_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('workout_type', sa.String(length=60), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_distance_meters', sa.Float(), nullable=True),
        sa.Column('target_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('target_pace_ms', sa.Float(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # conversation_messages
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_msg_conv', 'conversation_messages', ['conversation_id'])

    # ai_insights
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_type', sa.String(length=60), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('data_period_start', sa.String(length=20), nullable=True),
        sa.Column('data_period_end', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # sync_jobs
    op.create_table(
        'sync_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(length=30), nullable=False, server_default='official'),
        sa.Column('job_type', sa.String(length=20), nullable=False, server_default='incremental'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('records_synced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('last_synced_activity_id', sa.String(length=64), nullable=True),
        sa.Column('last_synced_date', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # provider_credentials
    op.create_table(
        'provider_credentials',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(length=30), nullable=False),
        sa.Column('access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('provider_credentials')
    op.drop_table('sync_jobs')
    op.drop_table('ai_insights')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('training_plan_days')
    op.drop_table('training_plans')
    op.drop_table('personal_records')
    op.drop_table('race_goals')
    op.drop_table('sleep_records')
    op.drop_table('daily_health_metrics')
    op.drop_table('activity_samples')
    op.drop_table('activity_laps')
    op.drop_table('activities')
    op.drop_table('user_profiles')
