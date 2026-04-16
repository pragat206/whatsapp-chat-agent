"""Initial schema.

Revision ID: 001
Revises: None
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # --- Roles ---
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("password_reset_token", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- User Roles ---
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE")),
    )

    # --- Contacts ---
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("phone_number", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(200), nullable=True),
        sa.Column("whatsapp_name", sa.String(200), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("language", sa.String(10), default="en"),
        sa.Column("tags", postgresql.JSONB, default={}),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_blocked", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Tags ---
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("color", sa.String(7), default="#6366f1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Product Categories ---
    op.create_table(
        "product_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(200), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_categories.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Products ---
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(300), nullable=False, index=True),
        sa.Column("sku", sa.String(100), unique=True, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Product Category Links ---
    op.create_table(
        "product_category_links",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE")),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_categories.id", ondelete="CASCADE")),
    )

    # --- AI Runs (must come before messages for FK) ---
    op.create_table(
        "ai_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer, default=0),
        sa.Column("completion_tokens", sa.Integer, default=0),
        sa.Column("total_tokens", sa.Integer, default=0),
        sa.Column("latency_ms", sa.Integer, default=0),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("system_prompt", sa.Text, nullable=True),
        sa.Column("user_input", sa.Text, nullable=True),
        sa.Column("ai_output", sa.Text, nullable=True),
        sa.Column("retrieved_chunks", postgresql.JSONB, default=[]),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("status", sa.String(20), default="active", index=True),
        sa.Column("state", sa.String(30), default="greeting"),
        sa.Column("is_ai_active", sa.Boolean, default=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("language", sa.String(10), default="en"),
        sa.Column("message_count", sa.Integer, default=0),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add FK from ai_runs to conversations
    op.create_foreign_key("fk_ai_runs_conversation", "ai_runs", "conversations", ["conversation_id"], ["id"])

    # --- Conversation Tags ---
    op.create_table(
        "conversation_tags",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE")),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE")),
    )

    # --- Messages ---
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False, index=True),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("message_type", sa.String(20), default="text"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("external_id", sa.String(255), nullable=True, index=True),
        sa.Column("is_ai_generated", sa.Boolean, default=False),
        sa.Column("ai_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_runs.id"), nullable=True),
        sa.Column("media_url", sa.String(1000), nullable=True),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Message Events ---
    op.create_table(
        "message_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("messages.id"), nullable=False, index=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("payload", postgresql.JSONB, default={}),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Handoff Events ---
    op.create_table(
        "handoff_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("initiated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("handoff_type", sa.String(50), default="manual"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Conversation Notes ---
    op.create_table(
        "conversation_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Leads ---
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("product_interest", sa.String(500), nullable=True),
        sa.Column("budget", sa.String(200), nullable=True),
        sa.Column("contact_preference", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), default="new"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("extra_fields", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Knowledge Sources ---
    op.create_table(
        "knowledge_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("original_filename", sa.String(500), nullable=True),
        sa.Column("content_text", sa.Text, nullable=True),
        sa.Column("url", sa.String(2000), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("chunk_count", sa.Integer, default=0),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Knowledge Chunks ---
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, default=0),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Embedding Records with pgvector ---
    op.create_table(
        "embedding_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("dimensions", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Add pgvector column
    op.execute("ALTER TABLE embedding_records ADD COLUMN embedding vector(1536)")
    op.execute("CREATE INDEX idx_embedding_vector ON embedding_records USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

    # --- Settings ---
    op.create_table(
        "settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("key", sa.String(200), unique=True, nullable=False, index=True),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column("value_json", postgresql.JSONB, nullable=True),
        sa.Column("category", sa.String(100), default="general"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Audit Logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(200), nullable=False, index=True),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", postgresql.JSONB, default={}),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Background Jobs ---
    op.create_table(
        "background_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_type", sa.String(100), nullable=False, index=True),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("payload", postgresql.JSONB, default={}),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed default roles
    op.execute("""
        INSERT INTO roles (id, name, description) VALUES
        (uuid_generate_v4(), 'super_admin', 'Full system access'),
        (uuid_generate_v4(), 'admin', 'Administrative access'),
        (uuid_generate_v4(), 'analyst', 'Read-only analytics access'),
        (uuid_generate_v4(), 'operator', 'Conversation and support access')
    """)


def downgrade() -> None:
    tables = [
        "background_jobs", "audit_logs", "settings", "embedding_records",
        "knowledge_chunks", "knowledge_sources", "leads", "conversation_notes",
        "handoff_events", "message_events", "messages", "conversation_tags",
        "ai_runs", "conversations", "product_category_links", "products",
        "product_categories", "tags", "contacts", "user_roles", "users", "roles",
    ]
    for table in tables:
        op.drop_table(table)
    op.execute("DROP EXTENSION IF EXISTS vector")
