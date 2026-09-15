"""baseline for existing users table"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "8156cca1c3ac"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # The users table already exists in the database.
    pass


def downgrade():
    # Keep the existing users table during baseline downgrade.
    pass