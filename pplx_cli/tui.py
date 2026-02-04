from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Markdown, Static, ScrollableContainer
from textual.containers import Vertical
from .client import client
from .history import HistoryManager
from .context import ContextLoader
import os

class PPLXTUI(App):
    CSS = """
    Screen {
        background: #121212;
    }
    #chat-scroll {
        height: 1fr;
        border: solid cyan;
        padding: 1;
        margin-bottom: 1;
    }
    #plan-view {
        height: 6;
        border: solid green;
        padding: 1;
        color: green;
        margin-bottom: 1;
    }
    Input {
        border: double bright_blue;
    }
    """

    def __init__(self):
        super().__init__()
        self.history_mgr = HistoryManager()
        self.history = self.history_mgr.load()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="chat-scroll"):
            yield Markdown("# Perplexity CLI v0.3\nDigite sua mensagem abaixo para começar.")
        yield Static(self.history_mgr.load_plan(), id="plan-view")
        yield Input(placeholder="Digite aqui... [Enter] para enviar", id="user-input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return

        input_widget = self.query_one("#user-input")
        input_widget.value = ""
        
        chat_scroll = self.query_one("#chat-scroll")
        chat_scroll.mount(Markdown(f"**Você:** {user_text}"))
        
        # Carrega contexto projeto + arquivos mencionados
        context = ContextLoader.get_full_context()
        full_query = f"{context}\n\nUSER QUERY: {user_text}"
        
        self.history.append({"role": "user", "content": full_query})
        
        # Feedback visual
        chat_scroll.mount(Markdown("*Perplexity está pensando...*"))
        chat_scroll.scroll_end()

        # Resposta da API
        response = client.chat(self.history)
        
        if response:
            # Remove o feedback visual de pensando e adiciona a resposta
            chat_scroll.query("Markdown").last().remove()
            chat_scroll.mount(Markdown(f"**Perplexity:**\n{response}"))
            self.history.append({"role": "assistant", "content": response})
            self.history_mgr.save(self.history)
            
            # Atualiza visão do plano
            self.query_one("#plan-view").update(self.history_mgr.load_plan())
        
        chat_scroll.scroll_end()

if __name__ == "__main__":
    app = PPLXTUI()
    app.run()