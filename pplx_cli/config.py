import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai"
MODEL = "sonar"
DEFAULT_MODEL = "sonar"
TEMPERATURE = 0.1
MAX_TOKENS = 4000

PPLX_PATH = "PPLX.md"
PLAN_PATH = "PLAN.md"
HISTORY_PATH = ".pplx_history.json"

SYSTEM_PROMPT = """Você é um engenheiro de software CLI sênior. 
Sua missão é ANALISAR o contexto do projeto, propor um PLANO detalhado e gerar CÓDIGO PRONTO.

Sempre responda EXATAMENTE neste formato:

## ANALISE
Explique o que foi entendido e os arquivos que serão afetados.

## PLANO
1. [ ] Passo 1
2. [ ] Passo 2

## CÓDIGO PRONTO
```python
# Arquivo: caminho/do/arquivo.py
conteúdo completo do arquivo aqui
```

NO FINAL DA RESPOSTA, SEMPRE ESCREVA: 
'Opções: 1.Criar 2.Editar 3.Continuar'"""