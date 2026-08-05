from app.providers.embedding_provider import EmbeddingProvider
from app.providers.llm import LLMProvider
from app.providers.vector_store import VectorStore
from app.services.prompt_builder import PromptBuilder
from app.services.retriever import Retriever


class ChatService:
    """
    End-to-end RAG chat service.
    """

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        llm: LLMProvider,
        model: str,
    ) -> None:

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = llm
        self.model = model

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Retrieve context, build prompt,
        generate an answer, and return sources.
        """

        contexts = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        prompt = self.prompt_builder.build(
            question=question,
            contexts=contexts,
        )

        answer = self.llm.generate(
            prompt=prompt,
            model=self.model,
        )

        return {
            "answer": answer,
            "sources": contexts,
        }