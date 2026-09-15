"""expand ecommerce backend from the existing users migration"""
from alembic import op
import sqlalchemy as sa

revision = "a9e7c2d1f444"
down_revision = "8156cca1c3ac"
branch_labels = None
depends_on = None


def _has_table(inspector, name):
    return name in inspector.get_table_names()


def _has_column(inspector, table, column):
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "users"):
        if not _has_column(inspector, "users", "is_active"):
            op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        if not _has_column(inspector, "users", "created_at"):
            op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
            op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            op.alter_column("users", "created_at", nullable=False)
    else:
        op.create_table("users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(20), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_email", "users", ["email"], unique=False)

    if not _has_table(inspector, "categories"):
        op.create_table("categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("name"),
        )
        op.create_index("ix_categories_name", "categories", ["name"], unique=False)

    if not _has_table(inspector, "products"):
        op.create_table("products",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price", sa.Numeric(12,2), nullable=False),
            sa.Column("stock", sa.Integer(), nullable=False),
            sa.Column("image_url", sa.String(500), nullable=True),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        )
        op.create_index("ix_products_id", "products", ["id"], unique=False)
        op.create_index("ix_products_name", "products", ["name"], unique=False)

    if not _has_table(inspector, "addresses"):
        op.create_table("addresses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("label", sa.String(50), nullable=False),
            sa.Column("line1", sa.String(255), nullable=False),
            sa.Column("line2", sa.String(255), nullable=True),
            sa.Column("city", sa.String(100), nullable=False),
            sa.Column("state", sa.String(100), nullable=False),
            sa.Column("postal_code", sa.String(20), nullable=False),
            sa.Column("country", sa.String(100), nullable=False),
            sa.Column("is_default", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_addresses_user_id", "addresses", ["user_id"], unique=False)

    if not _has_table(inspector, "cart_items"):
        op.create_table("cart_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        )
        op.create_index("ix_cart_items_user_id", "cart_items", ["user_id"], unique=False)
        op.create_index("ix_cart_items_product_id", "cart_items", ["product_id"], unique=False)

    if not _has_table(inspector, "orders"):
        op.create_table("orders",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("address_id", sa.Integer(), nullable=False),
            sa.Column("total_amount", sa.Numeric(12,2), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["address_id"], ["addresses.id"]),
        )
        op.create_index("ix_orders_id", "orders", ["id"], unique=False)
        op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)

    if not _has_table(inspector, "order_items"):
        op.create_table("order_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("product_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("unit_price", sa.Numeric(12,2), nullable=False),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        )
        op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)

    if not _has_table(inspector, "payments"):
        op.create_table("payments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Numeric(12,2), nullable=False),
            sa.Column("method", sa.String(50), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("provider_reference", sa.String(255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("order_id"),
        )


def downgrade():
    op.drop_table("payments")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_cart_items_product_id", table_name="cart_items")
    op.drop_index("ix_cart_items_user_id", table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index("ix_addresses_user_id", table_name="addresses")
    op.drop_table("addresses")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
