import click
import os
import subprocess
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from .client import client
from .history import HistoryManager
from .context import ContextLoader
from . import config

console = Console()
history_mgr = HistoryManager()

def handle_actions(resposta):
    """Lógica simplificada das 3 opções obrigatórias quando há código."""
    if not resposta:
        return

    # Se houver bloco de código ou definição de função
    if '```python' in resposta or 'def ' in resposta or 'class ' in resposta:
        console.print("\n[bold yellow]── Ações Disponíveis ──────────────────[/bold yellow]")
        console.print("1. [green]Criar arquivo com este código[/green]")
        console.print("2. [blue]Editar arquivo existente[/blue]")
        console.print("3. [white]Salvar PLAN.md e Continuar[/white]")
        
        choice = Prompt.ask(" Escolha [1/2/3]", choices=["1", "2", "3"], default="3")

        if choice == "1":
            # Tenta achar o nome do arquivo no texto ou pede
            match = re.search(r'#\s*(?:Arquivo|Nome do arquivo):\s*([\w\./-]+)', resposta)
            filename = match.group(1) if match else Prompt.ask("Nome do arquivo para criar")
            
            # Extrai o conteúdo do primeiro bloco de código encontrado
            code_match = re.search(r'```python\n(.*?)\n```', resposta, re.DOTALL)
            content = code_match.group(1) if code_match else resposta
            
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            console.print(f"[green]✅ Arquivo {filename} criado![/green]")
            os.system(f"code {filename}")

        elif choice == "2":
            filename = Prompt.ask("Qual arquivo deseja editar?")
            if os.path.exists(filename):
                os.system(f"code {filename}")
            else:
                console.print("[red]Arquivo não encontrado.[/red]")

    # Se houver um plano, salva no PLAN.md
    plan_match = re.search(r'## PLANO\n(.*?)(?=\n##|$)', resposta, re.DOTALL)
    if plan_match:
        plan_content = plan_match.group(1).strip()
        current_plan = history_mgr.load_plan()
        # Evita duplicar o mesmo plano se for exatamente igual
        if plan_content not in current_plan:
            new_plan = f"{current_plan}\n\n### Novo Passo\n{plan_content}"
            history_mgr.save_plan(new_plan)
            console.print("[dim green]✅ PLAN.md atualizado.[/dim green]")

@click.group(invoke_without_command=True)
@click.pass_context
@click.argument('query', required=False)
def main(ctx, query):
    if ctx.invoked_subcommand is None:
        if query:
            one_shot(query)
        else:
            tui()

@main.command()
def tui():
    """Abre a TUI ASCII"""
    from .tui import PPLXTUI
    app = PPLXTUI()
    app.run()

def one_shot(query):
    """Modo CLI direto com contexto e ações."""
    hist = history_mgr.load()
    project_ctx = ContextLoader.get_full_context()
    
    # Busca arquivos no prompt para carregar conteúdo
    files = re.findall(r'[\w\./-]+\.\w+', query)
    file_ctx = ""
    for f in set(files):
        file_ctx += ContextLoader.get_file_content(f)

    full_query = f"{project_ctx}\n{file_ctx}\nQUERY: {query}"
    hist.append({"role": "user", "content": full_query})
    
    with console.status("[bold cyan]Engenheiro Perplexity analisando..."):
        resposta = client.chat(hist)
    
    if resposta:
        console.print("\n" + "─" * 40)
        console.print(Markdown(resposta))
        console.print("─" * 40)
        
        hist.append({"role": "assistant", "content": resposta})
        history_mgr.save(hist)
        
        handle_actions(resposta)

@main.command()
@click.argument('query')
def ask(query):
    """Alias para fazer uma pergunta rápida"""
    one_shot(query)

if __name__ == '__main__':
    main()