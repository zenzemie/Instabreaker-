# InstaBreaker 2026

A modern, AI-driven Instagram tool designed for security researchers and enthusiasts.

## Features

- **Modern CLI**: Built with `Typer` and `Rich` for a beautiful terminal experience.
- **AI Wordlist Generation**: Personalized password generation using OpenAI's GPT-4o.
- **Session Management**: Cookie-based persistence to resume sessions or manage multiple accounts.
- **Async Engine**: High-performance networking using `httpx` and `asyncio`.
- **Termux Optimized**: Lightweight and compatible with Android/Termux environments.

## Installation

```bash
pip install .
```

## Usage

### Attack a target
```bash
instabreaker attack <username>
```

### Attack with AI wordlist
```bash
instabreaker attack <username> --ai
```

### Manage sessions
```bash
instabreaker sessions
```

### Configuration
```bash
instabreaker config --openai-key YOUR_API_KEY
```

## Disclaimer

This tool is for educational purposes only. The authors are not responsible for any misuse of this tool. Always obtain permission before testing any systems.
