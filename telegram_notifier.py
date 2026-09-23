import requests


TELEGRAM_MESSAGE_LIMIT = 3900


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str) -> None:
        for chunk in self._split_message(text):
            self._send_chunk(chunk)

    def _send_chunk(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": self.chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        response.raise_for_status()

    def _split_message(self, text: str) -> list[str]:
        if len(text) <= TELEGRAM_MESSAGE_LIMIT:
            return [text]

        chunks = []
        current_chunk = ""

        for paragraph in text.split("\n\n"):
            candidate = f"{current_chunk}\n\n{paragraph}".strip()

            if len(candidate) <= TELEGRAM_MESSAGE_LIMIT:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                if len(paragraph) <= TELEGRAM_MESSAGE_LIMIT:
                    current_chunk = paragraph
                else:
                    chunks.extend(
                        paragraph[i : i + TELEGRAM_MESSAGE_LIMIT]
                        for i in range(0, len(paragraph), TELEGRAM_MESSAGE_LIMIT)
                    )
                    current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
