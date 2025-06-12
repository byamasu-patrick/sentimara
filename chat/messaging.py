import asyncio
import logging

# TODO: Is the queue import needed?
import queue
from typing import Any, Dict, List, Optional
from uuid import uuid4

from anyio.streams.memory import MemoryObjectSendStream
from llama_index.agent.openai_agent import StreamingAgentChatResponse
from llama_index.callbacks.base import BaseCallbackHandler
from llama_index.callbacks.schema import CBEventType, EventPayload
from llama_index.query_engine.sub_question_query_engine import SubQuestionAnswerPair
from pydantic import BaseModel

import schema
from chat.engine import get_chat_engine
from libs.models.chatdb import MessageSubProcessSourceEnum
from schema import (
    Conversation,
    SubProcessMetadataKeysEnum,
    SubProcessMetadataMap,
    UserMessageCreate,
)

logger = logging.getLogger(__name__)


class StreamedMessage(BaseModel):
    """
    Represents a message to be streamed in the chat system.

    This class is used for holding the content of a message that is part of an ongoing chat conversation.

    Attributes:
    content (str): The textual content of the streamed message.
    """

    content: str


class StreamedMessageSubProcess(BaseModel):
    """
    Represents a subprocess within a streamed chat message.

    This class is used for holding information about a specific subprocess or event that occurs during the processing of a chat message.

    Attributes:
    source (MessageSubProcessSourceEnum): The source of the subprocess.
    has_ended (bool): Indicates whether the subprocess has ended.
    event_id (str): The unique identifier of the event.
    metadata_map (Optional[SubProcessMetadataMap]): Additional metadata associated with the subprocess.
    """

    source: MessageSubProcessSourceEnum
    has_ended: bool
    event_id: str
    metadata_map: Optional[SubProcessMetadataMap]


class ChatCallbackHandler(BaseCallbackHandler):
    """
    Handles callbacks for chat-related events.

    This class extends BaseCallbackHandler to provide custom handling of various chat events,
    such as the start and end of specific processes or actions within the chat system.

    Attributes:
    send_chan (MemoryObjectSendStream): A stream for sending messages or subprocess information.
    """

    def __init__(
        self,
        send_chan: MemoryObjectSendStream,
    ):
        """Initialize the base callback handler."""
        ignored_events = [CBEventType.CHUNKING, CBEventType.NODE_PARSING]
        super().__init__(ignored_events, ignored_events)
        self._send_chan = send_chan

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Create the MessageSubProcess row for the event that started."""
        asyncio.create_task(
            self.async_on_event(
                event_type, payload, event_id, is_start_event=True, **kwargs
            )
        )

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Create the MessageSubProcess row for the event that completed."""
        asyncio.create_task(
            self.async_on_event(
                event_type, payload, event_id, is_start_event=False, **kwargs
            )
        )

    def get_metadata_from_event(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        # TODO: Unused argument 'is_start_event'
        is_start_event: bool = False,
    ) -> SubProcessMetadataMap:
        """
        Extracts and returns metadata relevant to a specific chat event.

        This method processes the event payload to extract metadata based on the event type.
        It's particularly useful for handling sub-questions and augmenting the metadata map
        with structured information derived from these events.

        Parameters:
        event_type (CBEventType): The type of the chat event.
        payload (Optional[Dict[str, Any]]): The payload associated with the event, containing additional data.
        is_start_event (bool): Flag indicating whether the event is a start event.

        Returns:
        SubProcessMetadataMap: A dictionary containing the extracted metadata for the event.
        """
        metadata_map = {}

        if (
            event_type == CBEventType.SUB_QUESTION
            and EventPayload.SUB_QUESTION in payload
        ):
            sub_q: SubQuestionAnswerPair = payload[EventPayload.SUB_QUESTION]
            metadata_map[
                SubProcessMetadataKeysEnum.SUB_QUESTION.value
            ] = schema.QuestionAnswerPair.from_sub_question_answer_pair(sub_q).dict()
        return metadata_map

    async def async_on_event(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        is_start_event: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Asynchronously handles a specific chat event.

        This method is responsible for processing chat events asynchronously.
        It sends the processed event data, including metadata, to a designated stream channel
        for further handling or logging.

        Parameters:
        event_type (CBEventType): The type of the chat event.
        payload (Optional[Dict[str, Any]]): The payload associated with the event.
        event_id (str): The unique identifier of the event.
        is_start_event (bool): Flag indicating whether the event is a start event.
        **kwargs: Additional keyword arguments.
        """
        metadata_map = self.get_metadata_from_event(
            event_type, payload=payload, is_start_event=is_start_event
        )
        metadata_map = metadata_map or None
        source = MessageSubProcessSourceEnum[event_type.name]
        # TODO: Access to a protected member _closed of a client class
        if self._send_chan._closed:
            logger.debug("Received event after send channel closed. Ignoring.")
            return
        await self._send_chan.send(
            StreamedMessageSubProcess(
                source=source,
                metadata_map=metadata_map,
                event_id=event_id,
                has_ended=not is_start_event,
            )
        )

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """No-op."""

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """No-op."""


async def handle_chat_message(
    conversation: Conversation,
    user_message: UserMessageCreate,
    send_chan: MemoryObjectSendStream,
    temperature: float,
) -> None:
    """
    Handles the processing of a chat message within a conversation.

    This function manages the flow of processing a user's chat message. It sets up the chat engine,
    streams the chat response, and sends the processed message or a default response to the send channel.

    Parameters:
    conversation (Conversation): The conversation context in which the chat message is being processed.
    user_message (UserMessageCreate): The user message to be processed.
    send_chan (MemoryObjectSendStream): The stream channel to which the processed message or responses are sent.
    temperature (float): The temperature setting for the OpenAI model, controlling the creativity of the responses.
    """
    async with send_chan:
        chat_engine = await get_chat_engine(
            ChatCallbackHandler(send_chan), conversation, temperature
        )
        await send_chan.send(
            StreamedMessageSubProcess(
                event_id=str(uuid4()),
                has_ended=True,
                source=MessageSubProcessSourceEnum.CONSTRUCTED_QUERY_ENGINE,
            )
        )
        logger.debug("Engine received")
        templated_message = f"""
          Remember - if I have asked a relevant survey question, use the tables you have access to.  
            {user_message.content}
        """.strip()
        streaming_chat_response: StreamingAgentChatResponse = (
            await chat_engine.astream_chat(templated_message)
        )
        response_str = ""
        async for text in streaming_chat_response.async_response_gen():
            response_str += text
            # TODO: Access to a protected member _closed of a client class
            if send_chan._closed:
                logger.debug(
                    "Received streamed token after send channel closed. Ignoring."
                )
                return
            await send_chan.send(StreamedMessage(content=response_str))

        if response_str.strip() == "":
            await send_chan.send(
                StreamedMessage(
                    # content="Sorry, I either wasn't able to understand your question or I don't have an answer for it."
                    content="Sorry, I couldn't understand your question or don't have an answer. Could you please rephrase?"
                )
            )
