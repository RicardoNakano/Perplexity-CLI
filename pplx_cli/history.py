import json
import os
import tiktoken
from . import config

class HistoryManager:
    def __init__(self, history_file=".pplx_history.json"):
        self.history_file = history_file
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self, history):
        # Comprimir se necessário (> 6k tokens como no prompt)
        compressed = self.compress(history)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(compressed, f, indent=2, ensure_ascii=False)

    def count_tokens(self, messages):
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # cada mensagem tem um overhead
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
        return num_tokens

    def compress(self, history, max_tokens=6000):
        while self.count_tokens(history) > max_tokens and len(history) > 2:
            # Remove as mensagens mais antigas (mantendo o system prompt se houver)
            if history[0]["role"] == "system":
                history.pop(1)
            else:
                history.pop(0)
        return history

    def load_plan(self):
        if os.path.exists("PLAN.md"):
            with open("PLAN.md", 'r', encoding='utf-8') as f:
                return f.read()
        return "# PLAN.md\n\n## BACKLOG\n- [ ] Iniciar projeto\n"

    def save_plan(self, plan):
        with open("PLAN.md", 'w', encoding='utf-8') as f:
            f.write(plan)

    def load_project_context(self):
        context = ""
        if os.path.exists("PPLX.md"):
            with open("PPLX.md", 'r', encoding='utf-8') as f:
                context += f"\n--- PPLX.md ---\n{f.read()}\n"
        
        if os.path.exists("PLAN.md"):
            with open("PLAN.md", 'r', encoding='utf-8') as f:
                context += f"\n--- PLAN.md ---\n{f.read()}\n"
        
        return context