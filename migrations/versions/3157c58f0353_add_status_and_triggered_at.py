from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '3157c58f0353'
down_revision: Union[str, None] = 'a490e1fc45be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. יצירת ה-Enum ב-PostgreSQL לפני השימוש בו
    op.execute("CREATE TYPE alertstatus AS ENUM ('ACTIVE', 'PENDING', 'SENT', 'FAILED')")
    
    # 2. הוספת העמודות
    op.add_column('alerts', sa.Column('status', sa.Enum('ACTIVE', 'PENDING', 'SENT', 'FAILED', name='alertstatus'), nullable=False, server_default='ACTIVE'))
    op.add_column('alerts', sa.Column('last_triggered_at', sa.DateTime(), nullable=True))
    
    # 3. שינויי ה-Timezone (שאר הקוד שהיה לך)
    op.alter_column('alerts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('assets', 'last_updated',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)

def downgrade() -> None:
    # 1. החזרת שינויי ה-Timezone
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('assets', 'last_updated',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('alerts', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
               
    # 2. הסרת העמודות
    op.drop_column('alerts', 'last_triggered_at')
    op.drop_column('alerts', 'status')
    
    # 3. מחיקת ה-Type מה-DB
    op.execute("DROP TYPE alertstatus")