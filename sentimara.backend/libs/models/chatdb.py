from enum import Enum
from sqlalchemy import Column, DateTime, Numeric
from datetime import datetime
from llama_index.core.callbacks.schema import CBEventType
from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import relationship

from libs.models.base import Base


class MessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class MessageStatusEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class MessageSubProcessStatusEnum(str, Enum):
    PENDING = "PENDING"
    FINISHED = "FINISHED"


# python doesn't allow enums to be extended, so we have to do this
additional_message_subprocess_fields: dict[str, str] = {
    "CONSTRUCTED_QUERY_ENGINE": "constructed_query_engine",
    "SUB_QUESTIONS": "sub_questions",
}

MessageSubProcessSourceEnum = Enum(
    "MessageSubProcessSourceEnum",
    [(event_type.name, event_type.value) for event_type in CBEventType]
    + list(additional_message_subprocess_fields.items()),
)


def to_pg_enum(enum_class) -> ENUM:
    return ENUM(enum_class, name=enum_class.__name__)


class Document(Base):
    """
    A table along with its metadata
    """

    # URL to the actual document (e.g. a PDF)
    table_name = Column(String, nullable=False, unique=True)
    metadata_map = Column(JSONB, nullable=True)
    conversations = relationship("ConversationDocument", back_populates="document")

    class Config:
        from_attributes = True


class Conversation(Base):
    """
    A conversation with messages and linked documents
    """

    headline = Column(String, nullable=True, unique=False)
    messages = relationship("Message", back_populates="conversation")
    conversation_documents = relationship(
        "ConversationDocument", back_populates="conversation"
    )


class ConversationDocument(Base):
    """
    A many-to-many relationship between a conversation and a document
    """

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversation.id"), index=True
    )
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), index=True)
    conversation = relationship("Conversation", back_populates="conversation_documents")
    document = relationship("Document", back_populates="conversations")


class Message(Base):
    """
    A message in a conversation
    """

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversation.id"), index=True
    )
    content = Column(String)
    role = Column(to_pg_enum(MessageRoleEnum))
    temperature = Column(Float, default=0.1)
    status = Column(to_pg_enum(MessageStatusEnum), default=MessageStatusEnum.PENDING)
    conversation = relationship("Conversation", back_populates="messages")
    sub_processes = relationship("MessageSubProcess", back_populates="message")


class MessageSubProcess(Base):
    """
    A record of a sub-process that occurred as part of the generation of a message from an AI assistant
    """

    message_id = Column(UUID(as_uuid=True), ForeignKey("message.id"), index=True)
    source = Column(to_pg_enum(MessageSubProcessSourceEnum))
    message = relationship("Message", back_populates="sub_processes")
    status = Column(
        to_pg_enum(MessageSubProcessStatusEnum),
        default=MessageSubProcessStatusEnum.FINISHED,
        nullable=False,
    )
    metadata_map = Column(JSONB, nullable=True)


class HumanFeedback(Base):
    """
    A record of a human-feedback from the user to know whether they were satisfied with the response or not
    """

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    assistant_message_id = Column(UUID(as_uuid=True))
    user_message_id = Column(UUID(as_uuid=True))
    is_good_response = Column(Boolean)
    Thread_id = Column(UUID(as_uuid=True))



class Client(Base):
    __tablename__ = "clients"
    
    # Personal Details
    first_name = Column(String(100), nullable=False)
    client_number = Column(String(50), unique=True, nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    
    # Identification
    id_type = Column(String(50), nullable=True)
    id_number = Column(String(50), nullable=True)
    
    # Address
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Income
    annual_income = Column(Numeric(15, 2))
    income_currency = Column(String(3))
    
    # Nationality
    nationality = Column(String(100))
    
    # Relationship
    transactions = relationship("Transaction", back_populates="client")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_number = Column(String(50), unique=True, nullable=True)
    client_number = Column(String(50), ForeignKey('clients.client_number'), nullable=True)
    transaction_type = Column(String(50),nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    client = relationship("Client", back_populates="transactions")