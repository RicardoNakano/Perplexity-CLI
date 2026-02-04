import click
import os
import subprocess
import re
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from .client import client
from .history import HistoryManager
from . import config

console = Console()
history_mgr = HistoryManager()

def get_file_context(text):
    """Detecta arquivos mencionados no texto e retorna seu conteúdo."""
    files = re.findall(r'[\w\./-]+\.\w+', text)
    context = ""
    for f in set(files):
        if os.path.exists(f) and os.path.isfile(f):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    context += f"\n--- Conteúdo de {f} ---\n{file.read()}\n"
            except:
                pass
    return context

def apply_code_changes(response):
    """Extrai blocos de código da resposta e oferece para salvar/editar."""
    # Procura por blocos de código
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', response, re.DOTALL)
    
    for block in code_blocks:
        # Tenta identificar o nome do arquivo no bloco
        match = re.search(r'#\s*(?:Nome do arquivo|Arquivo):\s*([\w\./-]+)', block)
        if match:
            filename = match.group(1)
            if Confirm.ask(f"Deseja salvar as alterações em [bold cyan]{filename}[/bold cyan]?"):
                os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
                
                # Se for um diff (estilo Aider), poderíamos aplicar, mas por simplicidade vamos salvar o conteúdo
                content = re.sub(r'#\s*(?:Nome do arquivo|Arquivo):\s*[\w\./-]+\n', '', block).strip()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                console.print(f"[green]✅ {filename} atualizado![/green]")
                
                if Confirm.ask(f"Abrir {filename} no VS Code?"):
                    subprocess.run(["code", filename], shell=True)

def update_plan(response):
    """Extrai o plano da resposta e atualiza o PLAN.md."""
    plan_match = re.search(r'## PLANO\n(.*?)(?=\n##|$)', response, re.DOTALL)
    if plan_match:
        plan_content = plan_match.group(1).strip()
        if Confirm.ask("Deseja atualizar o PLAN.md?"):
            current_plan = history_mgr.load_plan()
            new_plan = f"{current_plan}\n\n### Novo Plano\n{plan_content}"
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
            chat()

@main.command()
def chat():
    """TUI Interativa com Histórico e Contexto"""
    hist = history_mgr.load()
    project_context = history_mgr.load_project_context()
    
    console.clear()
    console.print(Panel.fit(
        "      🚀 [bold cyan]Perplexity CLI[/bold cyan] 🚀      \n[dim]Contexto: PPLX.md + PLAN.md carregados",
        border_style="bright_blue"
    ))

    while True:
        user_input = Prompt.ask("\n[bold yellow]>[/bold yellow]")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
            
        # Adiciona contexto de arquivos mencionados
        file_ctx = get_file_context(user_input)
        full_query = f"{project_context}\n{file_ctx}\nUSER QUERY: {user_input}"
        
        hist.append({"role": "user", "content": full_query})
        
        with console.status("[bold green]Pensando..."):
            resposta = client.chat(hist)
        
        if resposta:
            console.print(f"\n[bold cyan]Perplexity[/bold cyan] ──────────────────────────")
            console.print(Markdown(resposta))
            console.print(f"──────────────────────────────────────────")
            
            hist.append({"role": "assistant", "content": resposta})
            history_mgr.save(hist)
            
            update_plan(resposta)
            apply_code_changes(resposta)
        else:
            console.print("[red]Erro ao obter resposta.[/red]")

def one_shot(query):
    """Executa uma query direta com contexto."""
    project_context = history_mgr.load_project_context()
    file_ctx = get_file_context(query)
    
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": f"{project_context}\n{file_ctx}\nQUERY: {query}"}
    ]
    
    with console.status("[bold green]Analisando..."):
        resposta = client.chat(messages)
    
    if resposta:
        console.print(Markdown(resposta))
        update_plan(resposta)
        apply_code_changes(resposta)

@main.command()
def tui():
    """Abre a interface TUI completa (Alias para chat)"""
    chat()

@main.command()
@click.argument('feature')
def plan(feature):
    """Cria um plano detalhado para uma nova funcionalidade no PLAN.md"""
    query = f"Crie um plano detalhado (checklist) para a seguinte funcionalidade: {feature}. Use o formato ## PLANO."
    one_shot(query)

@main.command()
@click.argument('filename')
def edit(filename):
    """Edita um arquivo específico com ajuda da IA"""
    if not os.path.exists(filename):
        console.print(f"[red]Arquivo {filename} não encontrado.[/red]")
        return
        
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    instrucao = Prompt.ask(f"O que deseja mudar em {filename}?")
    query = f"Edite o arquivo {filename}. Conteúdo atual:\n```\n{content}\n```\nInstrução: {instrucao}"
    one_shot(query)

if __name__ == '__main__':
    main()