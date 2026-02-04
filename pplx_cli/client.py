from openai import OpenAI
from rich.console import Console
from . import config
import os

console = Console()

class PerplexityClient:
    def __init__(self):
        self.api_key = config.API_KEY
        self.client = OpenAI(api_key=self.api_key, base_url=config.BASE_URL)

    def chat(self, messages, model=config.DEFAULT_MODEL):
        if not self.api_key:
            console.print("[red]Erro: PERPLEXITY_API_KEY não encontrada.[/red]")
            return None

        # Garante o System Prompt
        system_msg = {"role": "system", "content": config.SYSTEM_PROMPT}
        final_messages = [system_msg] + [m for m in messages if m["role"] != "system"]

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=final_messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]Erro API (OpenAI SDK): {e}[/red]")
            return None

    def summarize(self, history):
        prompt = "Resuma o histórico de chat abaixo mantendo os pontos principais e o estado atual do projeto:\n\n"
        for m in history:
            prompt += f"{m['role']}: {m['content'][:300]}...\n"
        
        messages = [{"role": "user", "content": prompt}]
        summary = self.chat(messages)
        return summary or "Resumo indisponível."

client = PerplexityClient()