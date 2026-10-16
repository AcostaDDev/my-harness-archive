"""P008-T011: conversación `project_import` del Flujo A con el inventario y el mapa congelados al crearla."""
from alembic import op
import sqlalchemy as sa

revision = '0019_import_conversations'
down_revision = '0018_conversation_keys'
branch_labels = None
depends_on = None


def upgrade():
    # Nullable: las conversaciones de definición y planificación no tienen origen que congelar.
    op.add_column('planning_conversations', sa.Column('source', sa.JSON(), nullable=True))


def downgrade():
    bind = op.get_bind()
    if (bind.execute(sa.text("SELECT count(*) FROM planning_conversations WHERE kind IN ('project_import', 'onboarding')")).scalar()
            or bind.execute(sa.text("SELECT count(*) FROM managed_runs WHERE purpose IN ('project_import', 'onboarding')")).scalar()):
        raise RuntimeError('Import/onboarding conversations cannot be represented before 0019; keep this revision')
    op.drop_column('planning_conversations', 'source')
