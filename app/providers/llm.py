from groq import Groq


class LLMProvider:
    """
    Wrapper around the Groq API.
    """

    def __init__(
        self,
        api_key: str,
    ) -> None:

        self.client = Groq(
            api_key=api_key,
        )

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> str:
        """
        Generate a response from the language model.
        """

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content