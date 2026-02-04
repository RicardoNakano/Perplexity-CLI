import click
import os
import subprocess
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from .client import client
from .history import HistoryManager
from .context import ContextLoader
from . import config

console = Console()
history_mgr = HistoryManager()

def handle_options(response):
    """Sempre oferece as 3 opções após uma resposta com código ou plano."""
    # Extrai blocos de código
    code_match = re.search(r'```python\n(?:# Arquivo: ([\w\./-]+)\n)?(.*?)\n```', response, re.DOTALL)
    plan_match = re.search(r'## PLANO\n(.*?)(?=\n##|$)', response, re.DOTALL)

    console.print("\n[bold yellow]Opções Disponíveis:[/bold yellow]")
    console.print("1. [bold green]Criar/Atualizar Arquivo[/bold green]")
    console.print("2. [bold blue]Editar Arquivo Existente[/bold blue]")
    console.print("3. [bold white]Salvar PLAN.md e Continuar[/bold white]")
    
    choice = Prompt.ask("Escolha uma ação", choices=["1", "2", "3"], default="3")

    if choice == "1" and code_match:
        filename = code_match.group(1) or Prompt.ask("Nome do arquivo para salvar")
        content = code_match.group(2).strip()
        
        os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        console.print(f"[green]✅ {filename} criado/atualizado![/green]")
        os.system(f"code {filename}")

    elif choice == "2":
        filename = Prompt.ask("Qual arquivo deseja editar?")
        if os.path.exists(filename):
            os.system(f"code {filename}")
            console.print(f"[blue]📝 {filename} aberto no VS Code.[/blue]")
        else:
            console.print("[red]Arquivo não encontrado.[/red]")

    if plan_match:
        plan_content = plan_match.group(1).strip()
        current_plan = history_mgr.load_plan()
        new_plan = f"{current_plan}\n\n### Atualização\n{plan_content}"
        history_mgr.save_plan(new_plan)
        console.print("[green]✅ PLAN.md atualizado![/green]")

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
    """Abre a interface TUI completa (Textual)"""
    from .tui import PPLXTUI
    app = PPLXTUI()
    app.run()

@main.command()
@click.argument('query')
def chat(query):
    """Alias para query rápida no terminal"""
    one_shot(query)

def one_shot(query):
    """Executa uma query com contexto total e oferece as 3 opções."""
    hist = history_mgr.load()
    context = ContextLoader.get_full_context()
    
    # Verifica se há arquivos mencionados para ler conteúdo
    files = re.findall(r'[\w\./-]+\.\w+', query)
    file_context = ""
    for f in set(files):
        file_context += ContextLoader.get_file_content(f)

    full_query = f"{context}\n{file_context}\nUSER QUERY: {query}"
    hist.append({"role": "user", "content": full_query})
    
    with console.status("[bold green]Analisando projeto..."):
        response = client.chat(hist)
    
    if response:
        console.print(Markdown(response))
        hist.append({"role": "assistant", "content": response})
        history_mgr.save(hist)
        handle_options(response)

@main.command()
@click.argument('feature')
def plan(feature):
    """Cria um plano detalhado para uma funcionalidade."""
    query = f"Crie um plano (checklist) para: {feature}"
    one_shot(query)

if __name__ == '__main__':
    main()
