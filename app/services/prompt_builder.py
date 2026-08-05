from typing import Any


class PromptBuilder:
    """
    Builds prompts for the language model.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful AI assistant. "
        "Answer the user's question using only the provided context. "
        "If the answer is not present in the context, say that you do not know."
    )

    def build(
        self,
        question: str,
        contexts: list[dict[str, Any]],
        system_prompt: str | None = None,
    ) -> str:
        """
        Build a complete prompt for the LLM.
        """

        prompt_system = (
            system_prompt
            if system_prompt
            else self.DEFAULT_SYSTEM_PROMPT
        )

        context_text = self._build_context(contexts)

        return (
            f"{prompt_system}\n\n"
            f"Context:\n"
            f"{context_text}\n\n"
            f"Question:\n"
            f"{question}"
        )

    def _build_context(
        self,
        contexts: list[dict[str, Any]],
    ) -> str:
        """
        Format retrieved chunks into a readable context block.
        """

        if not contexts:
            return "No relevant context found."

        lines: list[str] = []

        for index, item in enumerate(contexts, start=1):

            payload = item["payload"]

            document_id = payload["document_id"]
            chunk_number = payload["chunk_number"]
            text = payload["text"]

            lines.append(
                (
                    f"[Document {document_id} | "
                    f"Chunk {chunk_number}]\n"
                    f"{text}"
                )
            )

        return "\n\n".join(lines)