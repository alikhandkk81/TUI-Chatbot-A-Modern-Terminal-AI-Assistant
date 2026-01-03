import asyncio
from datetime import datetime
import textwrap
import os
import requests
import pyperclip

from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Input,
    Static,
    ListView,
    ListItem,
    Label,
)
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual import events

from rich.panel import Panel
from rich.text import Text


# ==============================
# CONFIG: OpenRouter backend
# ==============================

OPENROUTER_API_KEY = "" # your api
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# List of models to cycle through with "m"
OPENROUTER_MODELS = [
    "openai/gpt-4o-mini",
    "google/gemini-1.5-flash",
    "meta-llama/llama-3.1-8b-instruct",
]

DEFAULT_MODEL_INDEX = 0


async def ask_ai_async(messages, model: str):
    return await asyncio.to_thread(ask_ai_sync, messages, model)


def ask_ai_sync(messages, model: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "TUI Chatbot",
        "Content-Type": "application/json",
    }

    data = {"model": model, "messages": messages}

    response = requests.post(OPENROUTER_URL, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# ==============================
# UI widgets
# ==============================

class ChatMessage(Static):
    """A chat bubble with a live-updating body for streaming."""

    def __init__(self, text: str, is_user: bool):
        super().__init__()
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")

        # Create header and body widgets
        self.header_widget = Static()
        self.body_widget = Static()

        # Initial text
        self.body_text = text

    def compose(self):
        yield self.header_widget
        yield self.body_widget

    def on_mount(self):
        who = "You" if self.is_user else "Bot"
        avatar = "😃" if self.is_user else "🤖"
        color = "cyan" if self.is_user else "yellow"

        header = Text(f"{avatar} [{self.timestamp}] {who}", style=color)
        self.header_widget.update(header)

        self.update_body()

    def update_body(self):
        """Refresh the body text inside the bubble."""
        body = Text(self.body_text, style="white")
        border_color = "cyan" if self.is_user else "magenta"

        panel = Panel(
            body,
            border_style=border_color,
            padding=(0, 1),
        )
        self.body_widget.update(panel)

    def append_text(self, more: str):
        """Append text during streaming and refresh bubble."""
        self.body_text += more
        self.update_body()



class ChatView(VerticalScroll):
    """Scrollable container for chat bubbles."""
    pass


class TypingIndicator(Static):
    """Animated 'bot is typing' indicator."""
    dots = reactive("")

    def on_mount(self):
        self.set_interval(0.5, self.animate)
        self.display = False

    def animate(self):
        if not self.display:
            return
        self.dots = "." if self.dots == "..." else self.dots + "."
        self.update(f"[yellow]🤖 Bot is typing{self.dots}[/yellow]")


class ConversationItem(ListItem):
    """Sidebar item for a conversation."""

    def __init__(self, title: str, index: int):
        super().__init__(Label(title))
        self.index = index


# ==============================
# Main App
# ==============================

class ChatApp(App):
    # IMPORTANT: allow terminal to handle mouse selection for Ctrl+Shift+C copying
    MOUSE = False

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }

    #main {
        height: 1fr;
    }

    #sidebar {
        width: 30;
        border: round #555555;
    }

    #chat_container {
        border: round #555555;
    }

    ChatView {
        padding: 1 1;
    }

    Input {
        dock: bottom;
        border: tall #00afff;
        padding: 0 1;
    }

    TypingIndicator {
        height: 1;
        padding: 0 1;
    }

    .sidebar-title {
        padding: 1 1 0 1;
        color: #00afff;
    }

    .sidebar-help {
        padding: 0 1 1 1;
        color: #888888;
    }
    """

    BINDINGS = [
        ("t", "toggle_theme", "Toggle theme"),
        ("m", "cycle_model", "Switch model"),
        ("n", "new_conversation", "New conversation"),
        ("e", "export_conversation", "Export conversation"),
        ("c", "copy_bot", "Copy last bot message"),
        ("y", "copy_user", "Copy last user message"),
        ("ctrl+c", "copy_all", "Copy entire conversation"),
        ("q", "quit", "Quit"),
    ]

    dark_mode = reactive(True)
    current_conversation = reactive(0)
    current_model_index = reactive(DEFAULT_MODEL_INDEX)

    def __init__(self):
        super().__init__()
        # Each conversation: list of {"role": "user"/"assistant", "content": str}
        self.conversations = [[]]

    # -------------
    # Composition
    # -------------

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main"):
            with Vertical(id="sidebar"):
                self.sidebar_title = Static("Conversations", classes="sidebar-title")
                yield self.sidebar_title
                yield Static(
                    " To Select Options first click on terminal then [b]n[/b]=new  [b]m[/b]=model  [b]t[/b]=theme\n[b]e[/b]=export  [b]c/y/Ctrl+C[/b]=copy",
                    classes="sidebar-help",
                )
                self.sidebar_list = ListView()
                yield self.sidebar_list

            with Vertical(id="chat_container"):
                self.chat_view = ChatView()
                yield self.chat_view
                self.typing_indicator = TypingIndicator()
                yield self.typing_indicator

        self.input = Input(placeholder="Type your message and press Enter…")
        yield self.input

        yield Footer()

    async def on_mount(self):
        self.update_sidebar_title()
        self.refresh_sidebar()
        await self.load_conversation(0)
        self.input.focus()
        self.update_title()

    # -------------
    # Theme + model
    # -------------

    def update_title(self):
        model = OPENROUTER_MODELS[self.current_model_index]
        self.title = f"ChatApp [{model}]"

    def update_sidebar_title(self):
        model = OPENROUTER_MODELS[self.current_model_index]
        self.sidebar_title.update(f"Conversations\n[dim]{model}[/dim]")

    def action_toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.styles.background = "black" if self.dark_mode else "white"

    def action_cycle_model(self):
        self.current_model_index = (self.current_model_index + 1) % len(OPENROUTER_MODELS)
        self.update_title()
        self.update_sidebar_title()
        self.typing_indicator.update(f"[cyan]Switched model to {OPENROUTER_MODELS[self.current_model_index]}[/cyan]")

    # -------------
    # Sidebar / conversations
    # -------------

    def refresh_sidebar(self):
        self.sidebar_list.clear()
        for idx, conv in enumerate(self.conversations):
            if conv:
                first = conv[0]["content"].strip().replace("\n", " ")
                title = first[:20] + ("…" if len(first) > 20 else "")
            else:
                title = f"Conversation {idx + 1}"
            self.sidebar_list.append(ConversationItem(title, idx))

    async def load_conversation(self, index: int):
        # Clear chat safely for all Textual versions
        for child in list(self.chat_view.children):
            child.remove()

        # Reload messages
        for msg in self.conversations[index]:
            await self.add_message_widget(msg["content"], msg["role"] == "user", from_history=True)

    def action_new_conversation(self):
        self.conversations.append([])
        self.current_conversation = len(self.conversations) - 1
        self.refresh_sidebar()
        self.call_later(self.load_conversation, self.current_conversation)

    async def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if isinstance(item, ConversationItem):
            self.current_conversation = item.index
            await self.load_conversation(item.index)

    # -------------
    # Chat logic
    # -------------

    async def add_message_widget(self, text: str, is_user: bool, from_history: bool = False):
        widget = ChatMessage(text, is_user=is_user)
        self.chat_view.mount(widget)

        if hasattr(self.chat_view, "scroll_end"):
            try:
                self.chat_view.scroll_end(animate=not from_history)
            except TypeError:
                try:
                    self.chat_view.scroll_end()
                except TypeError:
                    pass

    async def on_input_submitted(self, event: Input.Submitted):
        content = event.value.strip()
        if not content:
            return

        event.input.value = ""

        conv = self.conversations[self.current_conversation]
        conv.append({"role": "user", "content": content})

        await self.add_message_widget(content, is_user=True)
        self.refresh_sidebar()

        self.typing_indicator.display = True
        asyncio.create_task(self.handle_bot_reply())

    async def handle_bot_reply(self):
        index = self.current_conversation
        conv = self.conversations[index]
        model = OPENROUTER_MODELS[self.current_model_index]

        try:
            full_reply = await ask_ai_async(conv, model)
        except Exception as e:
            full_reply = f"(Error: {e})"

        # Save to conversation history
        conv.append({"role": "assistant", "content": full_reply})

        # Only stream if user is still in this conversation
        if self.current_conversation == index:
            self.typing_indicator.display = False
            await self.stream_bot_reply(full_reply)

    async def stream_bot_reply(self, reply: str):
        """Smooth typewriter streaming effect."""
        widget = ChatMessage("", is_user=False)
        self.chat_view.mount(widget)

        chunk_size = 4  # smaller chunks = smoother typing
        for i in range(0, len(reply), chunk_size):
            widget.append_text(reply[i:i+chunk_size])

            # Scroll to bottom
            if hasattr(self.chat_view, "scroll_end"):
                try:
                    self.chat_view.scroll_end()
                except:
                    pass

            await asyncio.sleep(0.015)


    # -------------
    # Copy & export
    # -------------

    def action_copy_bot(self):
        conv = self.conversations[self.current_conversation]
        for msg in reversed(conv):
            if msg["role"] == "assistant":
                pyperclip.copy(msg["content"])
                self.typing_indicator.update("[green]Copied last bot message[/green]")
                return
        self.typing_indicator.update("[red]No bot message to copy[/red]")

    def action_copy_user(self):
        conv = self.conversations[self.current_conversation]
        for msg in reversed(conv):
            if msg["role"] == "user":
                pyperclip.copy(msg["content"])
                self.typing_indicator.update("[green]Copied last user message[/green]")
                return
        self.typing_indicator.update("[red]No user message to copy[/red]")

    def action_copy_all(self):
        conv = self.conversations[self.current_conversation]
        text = "\n\n".join(
            (f"You: {m['content']}" if m["role"] == "user" else f"Bot: {m['content']}")
            for m in conv
        )
        pyperclip.copy(text)
        self.typing_indicator.update("[green]Copied entire conversation[/green]")

    def action_export_conversation(self):
        conv = self.conversations[self.current_conversation]
        if not conv:
            self.typing_indicator.update("[red]Nothing to export[/red]")
            return

        text = "\n\n".join(
            (f"You: {m['content']}" if m["role"] == "user" else f"Bot: {m['content']}")
            for m in conv
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

        self.typing_indicator.update(f"[green]Exported to {filename}[/green]")

    # -------------
    # Keep focus on input
    # -------------

    async def on_key(self, event: events.Key):
        if event.key not in ("up", "down", "left", "right", "tab"):
            self.input.focus()


if __name__ == "__main__":
    ChatApp().run()

