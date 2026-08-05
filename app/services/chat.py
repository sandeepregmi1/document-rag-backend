from app.providers.llm import LLMProvider
from app.providers.redis_memory import RedisMemory
from app.services.prompt_builder import PromptBuilder
from app.services.retriever import Retriever


class ChatService:

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        llm: LLMProvider,
        redis_memory: RedisMemory,
        model: str,
    ) -> None:

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = llm
        self.redis_memory = redis_memory
        self.model = model

    def ask(
        self,
        session_id: str,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Complete RAG flow with memory.
        """

        history = self.redis_memory.load_history(
            session_id=session_id,
        )

        contexts = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        prompt = self.prompt_builder.build(
            question=question,
            contexts=contexts,
            history=history,
        )

        answer = self.llm.generate(
            prompt=prompt,
            model=self.model,
        )

        self.redis_memory.save_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        self.redis_memory.save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        return {
            "answer": answer,
            "sources": contexts,
            "history_size": len(history) + 2,
        }