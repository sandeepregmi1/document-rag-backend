from openai import OpenAI


class LLMProvider:

    def __init__(
        self,
        api_key: str,
    ):
        self.client = OpenAI(
            api_key=api_key,
        )

    def generate(
        self,
        prompt: str,
        model: str = "gpt-4.1-mini",
    ) -> str:

        response = self.client.responses.create(
            model=model,
            input=prompt,
        )

        return response.output_text