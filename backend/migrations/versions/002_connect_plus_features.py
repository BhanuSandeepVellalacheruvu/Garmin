"""Connect+ features: nutrition, trails, badges, sharing, live sessions

Revision ID: 002_connect_plus_features
Revises: 001_initial_schema
Create Date: 2026-10-25 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_connect_plus_features'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # nutrition_entries
    op.create_table(
        'nutrition_entries',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('meal_type', sa.String(length=30), nullable=False, server_default='snack'),
        sa.Column('food_name', sa.String(length=255), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('protein_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('carbs_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fat_g', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('water_ml', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_nutrition_user_date', 'nutrition_entries', ['user_id', 'entry_date'])

    # nutrition_targets
    op.create_table(
        'nutrition_targets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_calories', sa.Float(), nullable=False, server_default='2200.0'),
        sa.Column('target_protein_g', sa.Float(), nullable=False, server_default='140.0'),
        sa.Column('target_carbs_g', sa.Float(), nullable=False, server_default='250.0'),
        sa.Column('target_fat_g', sa.Float(), nullable=False, server_default='70.0'),
        sa.Column('target_water_ml', sa.Float(), nullable=False, server_default='2500.0'),
        sa.Column('active_from', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_nutrition_target_user', 'nutrition_targets', ['user_id'])

    # saved_trails
    op.create_table(
        'saved_trails',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_type', sa.String(length=50), nullable=False, server_default='running'),
        sa.Column('distance_meters', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('elevation_gain_meters', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('estimated_duration_seconds', sa.Float(), nullable=True),
        sa.Column('difficulty', sa.String(length=30), nullable=False, server_default='moderate'),
        sa.Column('surface_type', sa.String(length=50), nullable=False, server_default='trail'),
        sa.Column('start_lat', sa.Float(), nullable=True),
        sa.Column('start_lng', sa.Float(), nullable=True),
        sa.Column('waypoints_json', sa.JSON(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_trail_user_sport', 'saved_trails', ['user_id', 'activity_type'])

    # badge_milestones
    op.create_table(
        'badge_milestones',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='running'),
        sa.Column('tier', sa.String(length=30), nullable=False, server_default='bronze'),
        sa.Column('icon', sa.String(length=50), nullable=False, server_default='award'),
        sa.Column('achieved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('is_unlocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'badge_key', name='uq_badge_user_key'),
    )
    op.create_index('ix_badge_user_category', 'badge_milestones', ['user_id', 'category'])

    # activity_share_links
    op.create_table(
        'activity_share_links',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity_id', sa.String(length=36), sa.ForeignKey('activities.id', ondelete='CASCADE'), nullable=True),
        sa.Column('access_token', sa.String(length=64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('include_gps', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('include_hr', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('include_splits', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('views_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_share_user_activity', 'activity_share_links', ['user_id', 'activity_id'])

    # live_sessions
    op.create_table(
        'live_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sport', sa.String(length=50), nullable=False, server_default='running'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('elapsed_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('distance_meters', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_pace_sec', sa.Float(), nullable=True),
        sa.Column('current_heart_rate', sa.Integer(), nullable=True),
        sa.Column('avg_heart_rate', sa.Integer(), nullable=True),
        sa.Column('max_heart_rate', sa.Integer(), nullable=True),
        sa.Column('current_cadence', sa.Integer(), nullable=True),
        sa.Column('elevation_gain_m', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_power', sa.Integer(), nullable=True),
        sa.Column('telemetry_samples', sa.JSON(), nullable=True),
        sa.Column('emergency_contact_alerted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_ping_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_live_session_user_status', 'live_sessions', ['user_id', 'status'])


def downgrade() -> None:
    op.drop_table('live_sessions')
    op.drop_table('activity_share_links')
    op.drop_table('badge_milestones')
    op.drop_table('saved_trails')
    op.drop_table('nutrition_targets')
    op.drop_table('nutrition_entries')
