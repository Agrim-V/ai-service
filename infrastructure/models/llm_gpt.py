import os
from functools import lru_cache
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

class GPTBaseModel:
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    def load_llm(self) -> BaseChatModel:
        llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
        )
        return llm

class GPT35Model(GPTBaseModel):
    def __init__(self):
        super().__init__(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")

    @lru_cache(maxsize=1)
    def load_llm(self) -> BaseChatModel:
        return super().load_llm()

class GPT4oModel(GPTBaseModel):
    def __init__(self):
        super().__init__(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o")

    @lru_cache(maxsize=1)
    def load_llm(self) -> BaseChatModel:
        return super().load_llm()
