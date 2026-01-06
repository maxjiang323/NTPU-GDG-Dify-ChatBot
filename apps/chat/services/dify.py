import requests
import json
import os
from django.conf import settings

class DifyService:
    def __init__(self):
        self.api_key = os.getenv('DIFY_API_KEY')
        self.base_url = os.getenv('DIFY_API_URL')

    def stream_chat(self, query, user_id, conversation_id=None):
        if not self.api_key or not self.base_url:
            raise ValueError("Dify API credentials not configured in environment variables.")

        url = f"{self.base_url}/chat-messages"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": conversation_id or "",
            "user": user_id,
        }

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    try:
                        yield json.loads(decoded_line[5:])
                    except json.JSONDecodeError:
                        continue
