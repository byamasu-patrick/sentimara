import asyncio
import datetime
import logging
from collections import OrderedDict
from typing import Sequence
from uuid import UUID, uuid4

import anyio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

import schema
from api import crud
from api.deps import get_db
from chat.messaging import (
    StreamedMessage,
    StreamedMessageSubProcess,
    handle_chat_message,
)
from libs.models.chatdb import (
    Message,
    MessageRoleEnum,
    MessageStatusEnum,
    MessageSubProcess,
    MessageSubProcessStatusEnum,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/")
async def create_conversation(
    payload: schema.ConversationCreate,
    db: AsyncSession = Depends(get_db),
) -> schema.Conversation:
    """
    Create a new conversation
    """
    document_payload: schema.ConversationCreate = payload
    document_payload.document_ids = []

    documents: Sequence[schema.Document] = await crud.fetch_documents(
        db=db, table_names=payload.document_ids
    )  # type: ignore
    # print(documents)
    for document in documents:
        document_payload.document_ids.append(document.id)  # type: ignore

    return await crud.create_conversation(db, document_payload)


@router.post("/human-feedback")
async def create_human_feedback(
    payload: schema.HumanFeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> schema.HumanFeedbackResponse:
    """
    Create a new human feedback
    """
    response: schema.HumanFeedbackResponse = await crud.create_human_feedback(
        db=db, human_feedback_data=payload
    )  # type: ignore

    return response


@router.patch("/human-feedback/{human_feedback_id}")
async def update_human_feedback(
    human_feedback_id: UUID,
    payload: schema.HumanFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
) -> schema.HumanFeedbackResponse:
    """
    Create a new human feedback
    """
    if human_feedback_id == payload.id:
        response: schema.HumanFeedbackResponse = await crud.update_human_feedback(
            db=db, human_feedback_data=payload
        )  # type: ignore
        return response

    raise HTTPException(status_code=404, detail="Human feedback not found")


@router.put("/{conversation_id}")
async def update_conversation(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
) -> schema.Conversation:
    """
    Update a conversation by ID along with its first message.
    """
    conversation = await crud.update_conversation_headline(db, str(conversation_id))

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
) -> schema.Conversation:
    """
    Get a conversation by ID along with its messages and message subprocesses.
    """
    conversation = await crud.fetch_conversation_with_messages(db, str(conversation_id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete(
    "/{conversation_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_conversation(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation by ID.
    """
    did_delete = await crud.delete_conversation(db, str(conversation_id))  # type: ignore
    if not did_delete:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return


@router.get("/{conversation_id}/message")
async def message_conversation(
    conversation_id: UUID,
    user_message: str,
    temperature: float,
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    """
    Send a message from a user to a conversation, receive a SSE stream of the assistant's response.
    Each event in the SSE stream is a Message object. As the assistant continues processing the response,
    the message object's sub_processes list and content string is appended to. While the message is being
    generated, the status of the message will be PENDING. Once the message is generated, the status will
    be SUCCESS. If there was an error in processing the message, the final status will be ERROR.
    """
    conversation = await crud.fetch_conversation_with_messages(db, str(conversation_id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_messages = Message(
        created_at=datetime.datetime.utcnow(),  # type: ignore
        updated_at=datetime.datetime.utcnow(),  # type: ignore
        conversation_id=conversation_id,  # type: ignore
        temperature=temperature,  # type: ignore
        content=user_message,  # type: ignore
        role=MessageRoleEnum.user,  # type: ignore
        status=MessageStatusEnum.SUCCESS,  # type: ignore
    )  # type: ignore

    send_chan, recv_chan = anyio.create_memory_object_stream(1000)

    async def event_publisher():
        async with send_chan:
            task = asyncio.create_task(
                handle_chat_message(
                    conversation,
                    schema.UserMessageCreate(content=user_message),
                    send_chan,
                )
            )
            message_id = str(uuid4())
            message = Message(
                id=message_id,  # type: ignore
                conversation_id=conversation_id,  # type: ignore
                content="",  # type: ignore
                temperature=temperature,  # type: ignore
                role=MessageRoleEnum.assistant,  # type: ignore
                status=MessageStatusEnum.PENDING,  # type: ignore
                sub_processes=[],  # type: ignore
            )  # type: ignore
            final_status = MessageStatusEnum.ERROR
            event_id_to_sub_process = OrderedDict()
            try:
                async for message_obj in recv_chan:
                    if isinstance(message_obj, StreamedMessage):
                        message.content = message_obj.content  # type: ignore
                    elif isinstance(message_obj, StreamedMessageSubProcess):
                        status = (
                            MessageSubProcessStatusEnum.FINISHED
                            if message_obj.has_ended
                            else MessageSubProcessStatusEnum.PENDING
                        )
                        if message_obj.event_id in event_id_to_sub_process:
                            created_at = event_id_to_sub_process[
                                message_obj.event_id
                            ].created_at
                        else:
                            created_at = datetime.datetime.utcnow()
                        sub_process = MessageSubProcess(
                            created_at=created_at,  # type: ignore
                            message_id=message_id,  # type: ignore
                            source=message_obj.source,  # type: ignore
                            metadata_map=message_obj.metadata_map,  # type: ignore
                            status=status,  # type: ignore
                        )  # type: ignore
                        event_id_to_sub_process[message_obj.event_id] = sub_process

                        message.sub_processes = list(event_id_to_sub_process.values())
                    else:
                        logger.error(
                            f"Unknown message object type: {type(message_obj)}"
                        )
                        continue

                    validated_message = schema.Message.model_validate(
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

                    yield validated_message.model_dump_json()

                await task
                if task.exception():
                    raise ValueError(
                        "handle_chat_message task failed"
                    ) from task.exception()
                final_status = MessageStatusEnum.SUCCESS
            except:
                logger.error("Error in message publisher", exc_info=True)
                final_status = MessageStatusEnum.ERROR

            message.status = final_status  # type: ignore
            db.add(user_messages)
            db.add(message)
            await db.commit()

            final_message = await crud.fetch_message_with_sub_processes(db, message_id)
            yield final_message.json()  # type: ignore

    return EventSourceResponse(event_publisher())


@router.get("/{conversation_id}/regenerate")
async def regenerate_message(
    conversation_id: UUID,
    user_message: str,
    temperature: float,
    last_ai_message_id: str,
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    """
    Send a message from a user to a conversation, receive a SSE stream of the assistant's response.
    Each event in the SSE stream is a Message object. As the assistant continues processing the response,
    the message object's sub_processes list and content string is appended to. While the message is being
    generated, the status of the message will be PENDING. Once the message is generated, the status will
    be SUCCESS. If there was an error in processing the message, the final status will be ERROR.
    """
    conversation = await crud.fetch_conversation_with_messages(db, str(conversation_id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message: Message | None = await crud.get_message_with_sub_processes(
        db, last_ai_message_id
    )
    message.status = MessageStatusEnum.PENDING  # type: ignore
    message.content = ""  # type: ignore
    message.sub_processes = []  # type: ignore

    send_chan, recv_chan = anyio.create_memory_object_stream(1000)

    async def event_publisher():
        async with send_chan:
            task = asyncio.create_task(
                handle_chat_message(
                    conversation,
                    schema.UserMessageCreate(content=user_message),
                    send_chan,
                    last_ai_message_id,
                )
            )
            final_status = MessageStatusEnum.ERROR
            event_id_to_sub_process = OrderedDict()
            try:
                async for message_obj in recv_chan:
                    if isinstance(message_obj, StreamedMessage):
                        message.content = message_obj.content  # type: ignore
                    elif isinstance(message_obj, StreamedMessageSubProcess):
                        status = (
                            MessageSubProcessStatusEnum.FINISHED
                            if message_obj.has_ended
                            else MessageSubProcessStatusEnum.PENDING
                        )
                        if message_obj.event_id in event_id_to_sub_process:
                            created_at = event_id_to_sub_process[
                                message_obj.event_id
                            ].created_at
                        else:
                            created_at = datetime.datetime.utcnow()
                        sub_process = MessageSubProcess(
                            created_at=created_at,  # type: ignore
                            message_id=message.id,  # type: ignore
                            source=message_obj.source,  # type: ignore
                            metadata_map=message_obj.metadata_map,  # type: ignore
                            status=status,  # type: ignore
                        )  # type: ignore
                        event_id_to_sub_process[message_obj.event_id] = sub_process

                        message.sub_processes = list(event_id_to_sub_process.values())  # type: ignore
                    else:
                        logger.error(
                            f"Unknown message object type: {type(message_obj)}"
                        )
                        continue

                    validated_message = schema.Message.model_validate(
                        {
                            **message.__dict__,
                            "sub_processes": [
                                schema.MessageSubProcess.model_validate(
                                    sp if isinstance(sp, dict) else sp.__dict__
                                )
                                for sp in message.sub_processes  # type: ignore
                            ],
                        }
                    )

                    yield validated_message.model_dump_json()

                await task
                if task.exception():
                    raise ValueError(
                        "handle_chat_message task failed"
                    ) from task.exception()

                final_status = MessageStatusEnum.SUCCESS

            except asyncio.CancelledError:
                print("Stream canceled. Closing the channel gracefully.")
                raise
            except Exception as e:
                print(f"Error in message publisher: {e}")
                logger.error("Error in message publisher", exc_info=True)
                final_status = MessageStatusEnum.ERROR
                raise

            message.status = final_status  # type: ignore
            message.temperature = temperature  # type: ignore
            await db.commit()

            final_message = await crud.fetch_message_with_sub_processes(db, message_id=message.id)  # type: ignore

            yield final_message.json()  # type: ignore

    return EventSourceResponse(event_publisher())


@router.get("/{conversation_id}/test_message")
async def test_message_conversation(
    conversation_id: UUID,
    user_message: str,
    temperature: float,
    db: AsyncSession = Depends(get_db),
) -> schema.Message:
    """
    Test version of /message endpoint that returns a single message object instead of a SSE stream.
    """
    response: EventSourceResponse = await message_conversation(
        conversation_id,
        user_message,
        temperature,
        db,
    )
    final_message = None
    async for message in response.body_iterator:
        final_message = message
    if final_message is not None:
        return schema.Message.parse_raw(final_message)  # type: ignore
    else:
        raise HTTPException(status_code=500, detail="Internal server error")
