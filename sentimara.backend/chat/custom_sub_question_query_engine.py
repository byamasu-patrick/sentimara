import logging
from typing import Optional, Sequence

from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.llms.llm import LLM
from llama_index.core.query_engine.sub_question_query_engine import (
  SubQuestionQueryEngine,
)
from llama_index.core.question_gen.llm_generators import LLMQuestionGenerator
from llama_index.core.question_gen.types import BaseQuestionGenerator
from llama_index.core.response_synthesizers import (
  BaseSynthesizer,
  get_response_synthesizer,
)
from llama_index.core.settings import Settings
from llama_index.core.tools.query_engine import QueryEngineTool

logger = logging.getLogger(__name__)


class CustomSubQuestionQueryEngine(SubQuestionQueryEngine):
    """Custom Sub question query engine.

    A query engine that breaks down a complex query (e.g. compare and contrast) into
    many sub questions and their target query engine for execution.
    After executing all sub questions, all responses are gathered and sent to
    response synthesizer to produce the final response.

    Args:
        question_gen (BaseQuestionGenerator): A module for generating sub questions
            given a complex question and tools.
        response_synthesizer (BaseSynthesizer): A response synthesizer for
            generating the final response
        query_engine_tools (Sequence[QueryEngineTool]): Tools to answer the
            sub questions.
        verbose (bool): whether to print intermediate questions and answers.
            Defaults to True
        use_async (bool): whether to execute the sub questions with asyncio.
            Defaults to True
    """

    def __init__(
        self,
        question_gen: BaseQuestionGenerator,
        response_synthesizer: BaseSynthesizer,
        query_engine_tools: Sequence[QueryEngineTool],
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = True,
        use_async: bool = False,
    ) -> None:
        self._question_gen = question_gen
        self._response_synthesizer = response_synthesizer
        self._metadatas = [x.metadata for x in query_engine_tools]
        self._query_engines = {
            tool.metadata.name: tool.query_engine for tool in query_engine_tools
        }
        self._verbose = verbose
        self._use_async = use_async
        super().__init__(
            question_gen=question_gen,
            response_synthesizer=response_synthesizer,
            callback_manager=callback_manager,
            query_engine_tools=query_engine_tools,
            use_async=use_async,
            verbose=verbose,
        )

    @classmethod
    def from_defaults(
        cls,
        query_engine_tools: Sequence[QueryEngineTool],
        llm: Optional[LLM] = None,
        question_gen: Optional[BaseQuestionGenerator] = None,
        response_synthesizer: Optional[BaseSynthesizer] = None,
        verbose: bool = True,
        use_async: bool = True,
        callback_manager: Optional[CallbackManager] = None,
    ) -> "CustomSubQuestionQueryEngine":
        llm = llm or Settings.llm
        if question_gen is None:
            try:
                from llama_index.question_gen.openai import (  # pants: no-infer-dep
                  OpenAIQuestionGenerator,
                )

                # try to use OpenAI function calling based question generator.
                # if incompatible, use general LLM question generator
                question_gen = OpenAIQuestionGenerator.from_defaults(llm=llm)

            except ImportError as e:
                raise ImportError(
                    "`llama-index-question-gen-openai` package cannot be found. "
                    "Please install it by using `pip install `llama-index-question-gen-openai`"
                )
            except ValueError:
                question_gen = LLMQuestionGenerator.from_defaults(llm=llm)

        synth = response_synthesizer or get_response_synthesizer(
            llm=llm,
            callback_manager=callback_manager,
            use_async=use_async,
        )

        return cls(
            question_gen,
            synth,
            query_engine_tools,
            callback_manager=callback_manager,
            verbose=verbose,
            use_async=use_async,
        )
