
from llama_index.core.settings import _Settings
from llama_index.core.llms import LLM
from llama_index.core.llms.utils import resolve_llm, LLMType
from typing import Optional


class _CustomSettings(_Settings):
    """Custom settings."""
    # lazy initialization
    _code_llm: Optional[LLM] = None

    @property
    def code_llm(self) -> LLM:
        """Get the code LLM."""
        if self._code_llm is None:
            self._code_llm = resolve_llm("default")
        return self._code_llm

    @code_llm.setter
    def code_llm(self, llm: LLMType) -> None:
        """Set the code LLM."""
        self._code_llm = resolve_llm(llm)


        


CustomSettings = _CustomSettings()

