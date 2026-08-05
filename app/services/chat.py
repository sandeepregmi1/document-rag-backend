from app.providers.llm import LLMProvider
from app.providers.redis_memory import RedisMemory
from app.services.booking import BookingService
from app.services.prompt_builder import PromptBuilder
from app.services.retriever import Retriever


class ChatService:
    """
    Complete RAG chat service with
    Redis memory and interview booking.
    """

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        llm: LLMProvider,
        redis_memory: RedisMemory,
        booking_service: BookingService,
        model: str,
    ) -> None:

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = llm
        self.redis_memory = redis_memory
        self.booking_service = booking_service
        self.model = model

    def ask(
        self,
        session_id: str,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Complete chat flow.

        1. Check interview booking.
        2. If booking → save booking and return.
        3. Otherwise perform RAG.
        """

        history = self.redis_memory.load_history(
            session_id=session_id,
        )

        booking = self.booking_service.process(
            question,
        )

        if booking is not None:

            confirmation = (
                f"Interview booked successfully for "
                f"{booking.name} on "
                f"{booking.date} at "
                f"{booking.time}."
            )

            self.redis_memory.save_message(
                session_id=session_id,
                role="user",
                content=question,
            )

            self.redis_memory.save_message(
                session_id=session_id,
                role="assistant",
                content=confirmation,
            )

            return {
                "answer": confirmation,
                "sources": [],
                "is_booking": True,
                "history_size": len(history) + 2,
            }

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
            "is_booking": False,
            "history_size": len(history) + 2,
        }