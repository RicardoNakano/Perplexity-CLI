import json
import os
import tiktoken
from . import config
from .client import client

class HistoryManager:
    def __init__(self):
        self.history_file = config.HISTORY_PATH
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)[-10:] # Últimas 10 mensagens
            except:
                return []
        return []

    def save(self, history):
        if self.count_tokens(history) > 6000:
            summary = client.summarize(history)
            history = [
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "assistant", "content": f"Resumo do contexto anterior: {summary}"},
                history[-1] # Mantém a última
            ]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def count_tokens(self, messages):
        return sum(len(self.encoding.encode(m["content"])) for m in messages)

    def load_plan(self):
        if os.path.exists(config.PLAN_PATH):
            with open(config.PLAN_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        return "# PLAN.md\n"

    def save_plan(self, plan):
        with open(config.PLAN_PATH, 'w', encoding='utf-8') as f:
            f.write(plan)
