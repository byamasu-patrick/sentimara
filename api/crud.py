from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import schema
from chat.engine import get_conversation_headline
from libs.models.chatdb import (
    Conversation,
    ConversationDocument,
    Document,
    HumanFeedback,
    Message,
)


async def update_conversation_headline(
    db: AsyncSession, conversation_id: str
) -> Optional[schema.Conversation]:
    """
    Fetch a conversation with its first messages and
    Update the headline
    """
    # Eagerly load required relationships
    stmt = (
        select(Conversation)
        .options(joinedload(Conversation.messages))
        .options(joinedload(Conversation.conversation_documents))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(stmt)  # execute the statement
    conversation = result.scalars().first()  # get the first result

    if conversation is not None:
        messages = conversation.messages[0].content
        headline = get_conversation_headline(messages)

        print(headline)
        conversation.headline = headline  # type: ignore
        await db.commit()

        return conversation  # type: ignore

    return None


def find_previous_message(
    messages: List[schema.Message], target_id: str
) -> Optional[schema.Message]:
    prev_message = None
    for message in messages:
        if message.id == target_id:
            return prev_message
        prev_message = message
    return None


async def create_human_feedback(
    db: AsyncSession, human_feedback_data: schema.HumanFeedbackCreate
) -> Optional[schema.HumanFeedbackResponse]:

    human_feedback = HumanFeedback()
    human_feedback.assistant_message_id = human_feedback_data.assistant_message_id  # type: ignore
    human_feedback.is_good_response = human_feedback_data.is_good_response  # type: ignore
    human_feedback.conversation_id = human_feedback_data.conversation_id  # type: ignore

    conversation: schema.Conversation = await fetch_conversation_with_messages(db, str(human_feedback_data.conversation_id))  # type: ignore
    messages: List[schema.Message] = conversation.messages

    prev_message: schema.Message = find_previous_message(
        messages=messages, target_id=human_feedback_data.assistant_message_id  # type: ignore
    )  # type: ignore

    if prev_message:
        human_feedback.user_message_id = prev_message.id  # type: ignore

    db.add(human_feedback)
    await db.commit()
    await db.refresh(human_feedback)

    human_feedback_dict = human_feedback.__dict__

    return schema.HumanFeedbackResponse.model_validate(human_feedback_dict.__dict__)


async def update_human_feedback(
    db: AsyncSession, human_feedback_data: schema.HumanFeedbackUpdate
) -> Optional[schema.HumanFeedbackResponse]:

    # Retrieve the existing HumanFeedback object
    human_feedback = await db.get(HumanFeedback, human_feedback_data.id)
    if not human_feedback:
        return None  # Or handle it as per your error handling policy

    human_feedback.is_good_response = human_feedback_data.is_good_response  # type: ignore

    # Commit the changes to the database
    db.add(human_feedback)
    await db.commit()
    await db.refresh(human_feedback)

    human_feedback_dict = human_feedback.__dict__

    return schema.HumanFeedbackResponse.model_validate(human_feedback_dict.__dict__)


async def fetch_conversation_with_messages(
    db: AsyncSession, conversation_id: str
) -> Optional[schema.Conversation]:
    """
    Fetch a conversation with its messages + messagesubprocesses
    return None if the conversation with the given id does not exist
    """
    # Eagerly load required relationships
    stmt = (
        select(Conversation)
        .options(joinedload(Conversation.messages).subqueryload(Message.sub_processes))
        .options(
            joinedload(Conversation.conversation_documents).subqueryload(
                ConversationDocument.document
            )
        )
        .where(Conversation.id == conversation_id)
    )

    result = await db.execute(stmt)  # execute the statement
    conversation = result.scalars().first()  # get the first result
    if conversation is not None:
        # Prepare the dictionary for the conversation
        convo_dict = {
            **conversation.__dict__,
            "messages": [],
            "documents": [
                convo_doc.document.__dict__
                for convo_doc in conversation.conversation_documents
            ],
        }

        # Iterate through each message and validate
        for msg in conversation.messages:
            # Validate and convert sub_processes if necessary
            validated_sub_processes = [sp.__dict__ for sp in msg.sub_processes]

            # Update the message dictionary with validated sub_processes
            msg_dict = {**msg.__dict__, "sub_processes": validated_sub_processes}

            convo_dict["messages"].append(schema.Message.model_validate(msg_dict))

        return schema.Conversation.model_validate(convo_dict)

    return None


async def create_conversation(
    db: AsyncSession, convo_payload: schema.ConversationCreate
) -> schema.Conversation:
    conversation = Conversation()
    convo_doc_db_objects = [
        ConversationDocument(document_id=doc_id, conversation=conversation)  # type: ignore
        for doc_id in convo_payload.document_ids
    ]
    db.add(conversation)
    db.add_all(convo_doc_db_objects)
    await db.commit()
    await db.refresh(conversation)
    return await fetch_conversation_with_messages(db, conversation.id)  # type: ignore


async def fetch_message_with_sub_processes(
    db: AsyncSession, message_id: str
) -> Optional[schema.Message]:
    """
    Fetch a message with its sub processes
    return None if the message with the given id does not exist
    """
    # Eagerly load required relationships
    stmt = (
        select(Message)
        .options(joinedload(Message.sub_processes))
        .where(Message.id == message_id)
    )
    result = await db.execute(stmt)  # execute the statement
    message = result.scalars().first()  # get the first result
    if message is not None:
        return schema.Message.model_validate(
            {
                **message.__dict__,
                "sub_processes": [
                    schema.MessageSubProcess.model_validate(
                        sp if isinstance(sp, dict) else sp.__dict__
                    )
                    for sp in message.sub_processes
                ],
            }
        )
    return None


async def get_message_with_sub_processes(
    db: AsyncSession, message_id: str
) -> Optional[Message]:
    """
    Fetch a message with its sub processes
    return None if the message with the given id does not exist
    """
    # Eagerly load required relationships
    stmt = (
        select(Message)
        .options(joinedload(Message.sub_processes))
        .where(Message.id == message_id)
    )
    result = await db.execute(stmt)  # execute the statement
    message = result.scalars().first()  # get the first result
    return message


async def fetch_documents(
    db: AsyncSession,
    id: Optional[str] = None,
    ids: Optional[List[str]] = None,
    table_name: Optional[str] = None,
    table_names: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> Optional[Sequence[schema.Document]]:
    """
    Fetch a document by its url or id
    """

    stmt = select(Document)
    if id is not None:
        stmt = stmt.where(Document.id == id)
        limit = 1
    elif ids is not None:
        stmt = stmt.where(Document.id.in_(ids))
    if table_name is not None:
        stmt = stmt.where(Document.table_name == table_name)
    if table_names is not None:
        stmt = stmt.where(Document.table_name.in_(table_names))
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [schema.Document.model_validate(doc.__dict__) for doc in documents]


async def upsert_document_by_tablename(
    db: AsyncSession, document: schema.Document
) -> Optional[schema.Document]:
    """
    Upsert a document
    """
    stmt = insert(Document).values(**document.dict(exclude_none=True))
    stmt = stmt.on_conflict_do_update(
        index_elements=[Document.table_name],
        set_=document.dict(include={"metadata_map"}),
    )
    stmt = stmt.returning(Document)
    result = await db.execute(stmt)
    orm_obj = result.scalars().first()
    if orm_obj:
        orm_dict = orm_obj.__dict__
        upserted_doc = schema.Document.model_validate(orm_dict)
        await db.commit()
        return upserted_doc
    else:
        return None
