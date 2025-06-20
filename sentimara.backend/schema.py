"""
    Pydantic Schemas for the API
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from llama_index.core.callbacks.schema import EventPayload
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.core.query_engine.sub_question_query_engine import (
    SubQuestionAnswerPair,
)
from pydantic import BaseModel, Field, validator

from libs.models.chatdb import (
    MessageRoleEnum,
    MessageStatusEnum,
    MessageSubProcessSourceEnum,
    MessageSubProcessStatusEnum,
)


class QueryEngineInfo:
    def __init__(
        self,
        engine: SQLTableRetrieverQueryEngine,
        query_engine_description: str,
        top_query_engine_description: str,
    ):
        self.engine = engine
        self.query_engine_description = query_engine_description
        self.top_query_engine_description = top_query_engine_description


class TableInfo:
    def __init__(
        self,
        name: str,
        query_engine_description: str,
        top_query_engine_description: str,
    ):
        self.name = name
        self.query_engine_description = query_engine_description
        self.top_query_engine_description = top_query_engine_description


def build_uuid_validator(*field_names: str):
    return validator(*field_names)(lambda x: str(x) if x else x)  # type: ignore


class Base(BaseModel):
    id: Optional[UUID] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation datetime")
    updated_at: Optional[datetime] = Field(None, description="Update datetime")

    class Config:
        orm_mode = True


class BaseMetadataObject(BaseModel):
    class Config:
        orm_mode = True


class QuestionAnswerPair(BaseMetadataObject):
    """
    A question-answer pair that is used to store the sub-questions and answers
    """

    question: str
    answer: Optional[str]

    @classmethod
    def from_sub_question_answer_pair(
        cls, sub_question_answer_pair: SubQuestionAnswerPair
    ):
        return cls(
            question=sub_question_answer_pair.sub_q.sub_question,
            answer=sub_question_answer_pair.answer,
            # citations=citations,
        )


# later will be Union[QuestionAnswerPair, more to add later... ]
class SubProcessMetadataKeysEnum(str, Enum):
    SUB_QUESTION = EventPayload.SUB_QUESTION.value


# keeping the typing pretty loose here, in case there are changes to the metadata data formats.
SubProcessMetadataMap = Dict[Union[SubProcessMetadataKeysEnum, str], Any]


class MessageSubProcess(Base):
    message_id: UUID
    source: MessageSubProcessSourceEnum
    status: MessageSubProcessStatusEnum
    metadata_map: Optional[SubProcessMetadataMap]


class Message(Base):
    conversation_id: UUID
    content: str
    role: MessageRoleEnum
    temperature: float
    status: MessageStatusEnum
    sub_processes: List[MessageSubProcess]


class UserMessageCreate(BaseModel):
    content: str


class DocumentMetadataKeysEnum(str, Enum):
    """
    Enum for the keys of the metadata map for a document
    """

    COLLECTION_NAME = "collection_name"


DocumentMetadataMap = Dict[Union[DocumentMetadataKeysEnum, str], Any]


class Document(Base):
    table_name: str
    metadata_map: Optional[DocumentMetadataMap] = None


class Conversation(Base):
    messages: List[Message]
    documents: List[Document]


class ConversationCreate(BaseModel):
    # UUID
    document_ids: List[str]


class HumanFeedbackResponse(Base):
    assistant_message_id: UUID
    is_good_response: bool
    conversation_id: UUID


class HumanFeedbackUpdate(Base):
    is_good_response: bool


class HumanFeedbackCreate(Base):
    assistant_message_id: UUID
    is_good_response: bool
    conversation_id: UUID
