"""create default admin user

Revision ID: a3f0b4c9e012
Revises: c93ea1f83f27
Create Date: 2025-09-04 00:00:00.000000

"""

import os
from datetime import datetime

from alembic import op
import sqlalchemy as sa

# Reuse application helpers
from app.core.security import get_password_hash
from app.util.hash import get_rand_hash

# revision identifiers, used by Alembic.
revision = "a3f0b4c9e012"
down_revision = "c93ea1f83f27"
branch_labels = None
depends_on = None


def upgrade() -> None:
	conn = op.get_bind()

	admin_email = os.getenv("ADMIN_EMAIL", "admin@local")
	admin_password = os.getenv("ADMIN_PASSWORD", "admin")
	admin_name = os.getenv("ADMIN_NAME", "Administrator")

	# Check if a superuser already exists or the email already exists
	exists = conn.execute(
		sa.text('SELECT 1 FROM "user" WHERE email = :email OR is_superuser = :is_superuser LIMIT 1'),
		{"email": admin_email, "is_superuser": True},
	).first()

	if exists is None:
		now = datetime.utcnow()
		hashed = get_password_hash(admin_password)
		user_token = get_rand_hash()
		conn.execute(
			sa.text(
				'INSERT INTO "user" (created_at, updated_at, email, password, user_token, name, is_active, is_superuser) '
				'VALUES (:created_at, :updated_at, :email, :password, :user_token, :name, :is_active, :is_superuser)'
			),
			{
				"created_at": now,
				"updated_at": now,
				"email": admin_email,
				"password": hashed,
				"user_token": user_token,
				"name": admin_name,
				"is_active": True,
				"is_superuser": True,
			},
		)


def downgrade() -> None:
	conn = op.get_bind()
	admin_email = os.getenv("ADMIN_EMAIL", "admin@local")
	conn.execute(sa.text('DELETE FROM "user" WHERE email = :email'), {"email": admin_email})

