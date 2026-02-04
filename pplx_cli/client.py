import requests
from rich.console import Console
from . import config

console = Console()

class PerplexityClient:
    def __init__(self):
        self.api_key = config.API_KEY
        self.base_url = config.BASE_URL

    def chat(self, messages, model=config.DEFAULT_MODEL):
        if not self.api_key:
            console.print("[red]Erro: PERPLEXITY_API_KEY não encontrada.[/red]")
            return None

        # Garante o System Prompt
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
            "max_tokens": config.MAX_TOKENS
        }
        
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            console.print(f"[red]Erro API: {e}[/red]")
            return None

    def summarize(self, history):
        """Usa a API para resumir o histórico quando os tokens excedem o limite."""
        prompt = "Resuma o histórico de chat abaixo mantendo os pontos principais e o estado atual do projeto:\n\n"
        for m in history:
            prompt += f"{m['role']}: {m['content'][:500]}...\n"
        
        messages = [{"role": "user", "content": prompt}]
        summary = self.chat(messages)
        return summary or "Resumo indisponível."

client = PerplexityClient()