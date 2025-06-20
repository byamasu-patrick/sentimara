# Copy this entire content to your base.py file
from sqlalchemy import UUID, Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import uuid

@as_declarative()
class Base:
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    __name__: str

    # Generate __tablename__ automatically
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()