import requests
from rich.console import Console
import os
from . import config

console = Console()

class PerplexityClient:
    def __init__(self):
        self.api_key = config.API_KEY
        self.base_url = config.BASE_URL

    def chat(self, messages, model=config.DEFAULT_MODEL, stream=False):
        if not self.api_key:
            console.print("[red]Erro: PERPLEXITY_API_KEY não encontrada no .env[/red]")
            return None

        # Garante que o system prompt esteja presente
        if not any(m["role"] == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": config.TEMPERATURE,
            "max_tokens": config.MAX_TOKENS,
            "stream": stream,
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=data, 
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            console.print(f"[red]ERRO na API: {e}[/red]")
            return None

client = PerplexityClient()
