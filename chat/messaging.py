import asyncio
import logging

# TODO: Is the queue import needed?
from typing import Any, Dict, List, Optional
from uuid import uuid4

from anyio.streams.memory import MemoryObjectSendStream
from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload
from llama_index.core.chat_engine.types import StreamingAgentChatResponse
from llama_index.core.query_engine.sub_question_query_engine import (
    SubQuestionAnswerPair,
)
from pydantic import BaseModel

import schema
from chat.engine import get_chat_engine, workflow_runner
from libs.models.chatdb import MessageSubProcessSourceEnum
from schema import (
    Conversation,
    SubProcessMetadataKeysEnum,
    SubProcessMetadataMap,
    UserMessageCreate,
)
from .workflow import (    
    ProgressEvent,
    ToolRequestEvent,
    ToolApprovedEvent,
)
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
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
    ) -> str:  # type: ignore
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

        if event_type == CBEventType.SUB_QUESTION:

            print(f"Event Type: {event_type}")
            print(f"Event Payload: {payload}")  # type: ignore
            print(
                "--------------------------------------------------------------------------------------------------------------------------"
            )

        if (
            event_type == CBEventType.SUB_QUESTION
            and EventPayload.SUB_QUESTION in payload  # type: ignore
        ):
            sub_q: SubQuestionAnswerPair = payload[EventPayload.SUB_QUESTION]  # type: ignore
            metadata_map[SubProcessMetadataKeysEnum.SUB_QUESTION.value] = (
                schema.QuestionAnswerPair.from_sub_question_answer_pair(sub_q).dict()
            )
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
    last_ai_message_id: Optional[str] = None,
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
        await send_chan.send(
            StreamedMessageSubProcess(
                event_id=str(uuid4()),
                has_ended=True,
                metadata_map=None,
                source=MessageSubProcessSourceEnum.CONSTRUCTED_QUERY_ENGINE,  # type: ignore
            )  # type: ignore
        )
        logger.debug("Engine received")
        templated_message = f"""
            {user_message.content}
        """.strip()
        handler = await workflow_runner(
            ChatCallbackHandler(send_chan), templated_message, conversation, last_ai_message_id
        )

        response_str = ""
        async for event in handler.stream_events():
            # response_str += event.content
            if isinstance(event, StopEvent):
                if event.result:
                    response_str += event.result["response"]

                    print("<--- Final Response --->")
                    print(event.result["response"])
                    print("<--- Final Response --->")
            # elif isinstance(event, AgentInput):
            #     print("📥 Input:", event.input)
            elif isinstance(event, ToolApprovedEvent):
                if event.response:
                    print("📤 Output:", event.response)
                if event.tool_kwargs:
                    print(
                        "🛠️  Planning to use tools:",
                        [call.get("tool_name")   for call in event.tool_kwargs],
                    )

            elif isinstance(event, ToolRequestEvent):
                print(f"🔧 Tool Request ({event.tool_name}):")
                print(f"  Arguments: {event.tool_kwargs}")
            elif isinstance(event, ProgressEvent):
                print(f"Progress: {event.msg}")

            # if send_chan._closed:
            #     logger.debug(
            #         "Received streamed token after send channel closed. Ignoring."
            #     )
            #     return
            # response_str += event.response.content
            await send_chan.send(StreamedMessage(content=response_str))

        if response_str.strip() == "":
            await send_chan.send(
                StreamedMessage(
                    # content="Sorry, I either wasn't able to understand your question or I don't have an answer for it."
                    content="Sorry, I couldn't understand your question or don't have an answer. Could you please rephrase?"
                )
            )
