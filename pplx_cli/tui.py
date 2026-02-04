from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Markdown, Static, ScrollableContainer
from textual.containers import Container, Vertical
from textual.binding import Binding
from .client import client
from .history import HistoryManager
from .context import ContextLoader
import os

class PPLXTUI(App):
    CSS = """
    Screen {
        background: #1e1e1e;
    }
    #chat-container {
        height: 70%;
        border: solid cyan;
        padding: 1;
        margin: 1;
    }
    #plan-container {
        height: 20%;
        border: solid green;
        padding: 1;
        margin: 1;
        color: green;
    }
    Input {
        dock: bottom;
        margin: 1;
        border: double bright_blue;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("ctrl+l", "clear", "Limpar Chat"),
    ]

    def __init__(self):
        super().__init__()
        self.history_mgr = HistoryManager()
        self.history = self.history_mgr.load()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(id="chat-container")
        yield Static(self.history_mgr.load_plan(), id="plan-container")
        yield Input(placeholder="Digite aqui... [Enter] para enviar", id="user-input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return

        input_widget = self.query_one("#user-input")
        input_widget.value = ""
        
        chat_container = self.query_one("#chat-container")
        chat_container.mount(Markdown(f"**Você:** {user_text}"))
        
        # Carrega contexto
        context = ContextLoader.get_full_context()
        full_query = f"{context}\n\nUSER QUERY: {user_text}"
        
        self.history.append({"role": "user", "content": full_query})
        
        # Resposta da API
        response = client.chat(self.history)
        
        if response:
            chat_container.mount(Markdown(f"**Perplexity:**\n{response}"))
            self.history.append({"role": "assistant", "content": response})
            self.history_mgr.save(self.history)
            
            # Atualiza visão do plano se mudou
            self.query_one("#plan-container").update(self.history_mgr.load_plan())
        
        chat_container.scroll_end()

if __name__ == "__main__":
    app = PPLXTUI()
    app.run()
