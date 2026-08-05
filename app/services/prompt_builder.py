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
        history: list[dict] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """
        Build final prompt.
        """

        prompt_system = (
            system_prompt
            if system_prompt
            else self.DEFAULT_SYSTEM_PROMPT
        )

        history_text = self._build_history(
            history or []
        )

        context_text = self._build_context(
            contexts
        )

        return (
            f"{prompt_system}\n\n"
            f"Conversation History:\n"
            f"{history_text}\n\n"
            f"Context:\n"
            f"{context_text}\n\n"
            f"Question:\n"
            f"{question}"
        )

    def _build_history(
        self,
        history: list[dict],
    ) -> str:

        if not history:
            return "No previous conversation."

        lines = []

        for item in history:
            role = item["role"]
            content = item["content"]

            lines.append(
                f"{role}: {content}"
            )

        return "\n".join(lines)

    def _build_context(
        self,
        contexts: list[dict[str, Any]],
    ) -> str:

        if not contexts:
            return "No relevant context found."

        lines = []

        for item in contexts:

            lines.append(
                (
                    f"[Document {item['document_id']} | "
                    f"Chunk {item['chunk_number']}]\n"
                    f"{item['text']}"
                )
            )

        return "\n\n".join(lines)