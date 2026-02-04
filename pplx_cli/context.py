import os
from . import config

class ContextLoader:
    @staticmethod
    def get_full_context():
        context = ""
        if os.path.exists(config.PPLX_PATH):
            with open(config.PPLX_PATH, 'r', encoding='utf-8') as f:
                context += f"\n--- PROJETO (PPLX.md) ---\n{f.read()}\n"
        
        if os.path.exists(config.PLAN_PATH):
            with open(config.PLAN_PATH, 'r', encoding='utf-8') as f:
                context += f"\n--- PLANO ATUAL (PLAN.md) ---\n{f.read()}\n"
        
        return context

    @staticmethod
    def get_file_content(filepath):
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f"\n--- Arquivo: {filepath} ---\n{f.read()}\n"
            except:
                return ""
        return ""

