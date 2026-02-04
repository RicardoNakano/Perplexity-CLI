import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai"
MODEL = "sonar"

MODELS = {
    "cheap": "sonar",
    "pro": "sonar-pro",
    "large": "llama-3.1-sonar-large-128k-online",
    "small": "llama-3.1-sonar-small-128k-online"
}

DEFAULT_MODEL = MODELS["cheap"]
TEMPERATURE = 0.1
MAX_TOKENS = 4000

SYSTEM_PROMPT = """Você é um assistente de programação CLI avançado. 
Sua missão é ANALISAR o contexto do projeto, propor um PLANO e gerar CÓDIGO.

Sempre siga este formato de resposta:

## ANALISE
Breve explicação do que foi entendido e dos arquivos afetados.

## PLANO
1. [ ] Passo 1
2. [ ] Passo 2

## CÓDIGO
```python
# Nome do arquivo: caminho/do/arquivo.py
conteúdo aqui
```

Se precisar editar um arquivo existente, use o formato:
```python:diff
# Arquivo: caminho/do/arquivo.py
<<<<<<< SEARCH
código antigo
=======
código novo
>>>>>>> REPLACE
```
"""
