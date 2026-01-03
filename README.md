🌟 TUI Chatbot — A Modern Terminal AI Assistant

A fast, elegant, and developer‑friendly terminal-based AI chat client built with Python, Textual, Rich, and OpenRouter.
Designed for power users who prefer the keyboard, love clean UI, and want AI directly inside their terminal.

![Screenshot](img1.svg)
![Screenshot](img2.svg)

This project demonstrates:

    Real‑time streaming (typewriter effect)

    Custom TUI components

    Multi‑model LLM integration

    Async architecture

    Developer‑tool design

    Clean software structure

Perfect for learning, extending, or using as your daily AI assistant.

🚀 Features
🧠 Multi‑Model Support

Switch instantly between multiple OpenRouter models:

    GPT‑4o‑mini

    Gemini Flash

    Llama 3.1

    And any other OpenRouter model you add

Press m to cycle models.

⚡ Real‑Time Streaming (Typewriter Effect)

Bot responses appear smoothly, chunk by chunk, just like a real AI typing.
Built with a custom streaming engine and live‑updating bubble widget.
💬 Bubble‑Style Chat UI

Readable, modern chat bubbles with:

    Avatars

    Timestamps

    Color-coded roles

    Rich text rendering

    Auto-expanding layout

🗂 Multiple Conversations

A sidebar lets you:

    Switch between chats

    Create new conversations

    Auto‑generate titles

    Keep your history organized

🎨 Dark/Light Themes

Toggle instantly with t.
📁 Export Conversations

Save any conversation to a timestamped .txt file with e.

📋 Copy Messages

    c → Copy last bot message

    y → Copy last user message

    Ctrl+C → Copy entire conversation (inside the app)

    Mouse select + Ctrl+Shift+C → Copy to system clipboard

🖥 Terminal‑Native Experience

    Works in any Linux/macOS terminal

    Keyboard‑driven

    Smooth scrolling

    No mouse required (but supported)

📦 Installation

Clone the repository:

git clone https://github.com/YOURNAME/tui-chatbot.git cd tui-chatbot

Install dependencies:
pip install -r requirements.txt

🔑 Setup

Set your OpenRouter API key:
OPENROUTER_API_KEY = ""

⌨️ Keybindings

  Key	Action
  Enter	Send message
  m	Switch model
  t	Toggle theme
  n	New conversation
  e	Export conversation
  c	Copy last bot message
  y	Copy last user message
  Ctrl+C	Copy entire conversation (inside app)
  q	Quit

🛠 Tech Stack

    Python 3.10+

    Textual — Terminal UI framework

    Rich — Beautiful text rendering

    OpenRouter API — Multi‑model LLM backend

    Asyncio — Concurrency

    Pyperclip — Clipboard integration

🌱 Why This Project Matters

This project demonstrates:

    AI engineering

    Backend API integration

    Terminal UI design

    Async programming

    Software architecture

    Developer‑tool craftsmanship

It’s a strong portfolio piece for:

    AI Engineer

    Python Developer

    Backend Developer

    Tools Engineer

    Open‑Source Contributor

🤝 Contributing

Contributions are welcome!
Feel free to open issues, suggest features, or submit pull requests.

🏁 Usage

Run the app:
python tui_chatbot.py
python3 tui_chatbot.py
