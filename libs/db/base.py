# Import all the models, so that Base has them before being
# imported by Alembic
from models.base import Base  # noqa
from models.chatdb import *  # noqa
from models.db import *  # noqa
