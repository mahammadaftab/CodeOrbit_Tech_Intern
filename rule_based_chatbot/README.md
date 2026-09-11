# Rule-Based Chatbot (OrbitBot)

A modern, full-featured rule-based conversational chatbot written in Python. It supports both an **interactive terminal (CLI)** experience and a **rich, responsive web application** built with Flask and modern Vanilla CSS (featuring sleek cosmic dark mode, glassmorphism, glowing accents, real-time typing indicators, audio chimes, and a live rule inspector).

---

## Web Application Preview

The web interface provides an interactive, state-of-the-art UI for chatting with OrbitBot:

- **Cosmic Dark Theme & Glassmorphism**: Clean layout with frosted glass containers, dynamic ambient glow effects, and modern typography (`Outfit` and `Plus Jakarta Sans`).
- **Real-Time Rule Transparency**: Every bot response displays a color-coded tag indicating which rule triggered the reply (`Greeting`, `Time`, `Capabilities`, `Joke`, `Fallback`, `Exit`).
- **Interactive Rule Inspector**: A modal listing all compiled regex patterns, categories, and rule logic.
- **Dynamic Prompt Chips**: One-click quick-action chips for instant conversation prompts.
- **Audio Chimes**: Subtle, synthesized audio feedback on message send and receive (using Web Audio API, with a mute toggle).
- **Responsive Design**: Adapts cleanly across desktop, tablet, and mobile screens.

---

## How the Chatbot Decides Its Responses

OrbitBot uses a deterministic 5-step decision pipeline:

```
[User Input]
     │
     ▼
[Step 1: Input Validation] ──── (Empty/Whitespace) ──► Prompt for input
     │
     ▼
[Step 2: Normalization] (Lowercase, clean spacing, strip punctuation)
     │
     ▼
[Step 3: Exit Detection] ──── (Matched exit command) ──► Parting message & Terminate
     │
     ▼
[Step 4: Rule & Pattern Evaluation] (Sequential check of defined regex patterns)
     ├──► Greeting Rule          ──► Return friendly greeting (Tag: GREETING)
     ├──► Identity & Status Rule ──► Return bot info / status (Tag: IDENTITY)
     ├──► Capabilities & Help   ──► Return capabilities / guide (Tag: CAPABILITIES / HELP)
     ├──► Dynamic Time / Date   ──► Call dynamic datetime handler (Tag: TIME / DATE)
     └──► Joke & Entertainment  ──► Return tech joke (Tag: JOKE)
     │
     ▼ (No rule matched)
[Step 5: Fallback Mechanism] ──► Select helpful fallback response (Tag: FALLBACK)
```

### Detailed Decision Logic:
1. **Normalization**: Before matching, user inputs like `"  Hello, OrbitBot?!  "` are normalized to `"hello orbitbot"`. This eliminates failures caused by varying casing, trailing question marks, exclamation points, or erratic spacing.
2. **Prioritized Rules**:
   - Exit commands (`bye`, `quit`, `exit`, `see you`) are evaluated first to cleanly end sessions.
   - Core conversational intents are checked using regex word boundaries (`\b`) to prevent false positives (e.g., matching `"hi"` inside `"this"` is prevented).
   - Dynamic handlers query the system clock in real-time so that date and time answers are always current.
   - Canned responses are randomly selected from curated response pools for natural conversational variation.
3. **Fallback Handling**: If none of the regex patterns match the user's message, the bot activates its fallback system, acknowledging that the input is unrecognized and suggesting phrases or the `help` command.

---

## Project Structure

```
rule_based_chatbot/
├── app.py              # Flask web server & REST API
├── chatbot.py          # Core rule engine, pattern definitions, normalization & CLI loop
├── test_chatbot.py     # Comprehensive automated unit test suite
├── static/
│   ├── style.css       # Pure Vanilla CSS design system (dark mode, glassmorphism)
│   └── app.js          # Interactive JavaScript client (async chat, audio, modal)
├── templates/
│   └── index.html      # Accessible, modern HTML5 chat interface
└── README.md           # Project documentation and instructions
```

---

## Getting Started

### Prerequisites
- Python 3.8 or higher installed.
- Flask (already installed or install via `pip install flask`).

---

### Option 1: Running the Web Application (Recommended)

1. Start the Flask server:
   ```bash
   python rule_based_chatbot/app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. Chat with OrbitBot, click suggestion pills, inspect rules, and test various queries!

---

### Option 2: Running via Terminal (CLI)

Run the standalone CLI chat loop:
```bash
python rule_based_chatbot/chatbot.py
```

#### Sample Terminal Interaction
```text
============================================================
       Welcome to OrbitBot - Rule-Based Chatbot
============================================================
Type your message below and press Enter.
Type 'help' to see what I can do, or 'exit' / 'bye' to quit.

You: Hello!
OrbitBot: Hi there! Good to meet you. What's on your mind?

You: What is your name?
OrbitBot: My name is OrbitBot! I'm a rule-based Python chatbot designed to answer questions based on predefined rules.

You: What time is it?
OrbitBot: The current time is 06:37 PM.

You: Tell me a joke!
OrbitBot: Why do programmers prefer dark mode? Because light attracts bugs!

You: Can you fly a spaceship?
OrbitBot: I am a rule-based bot and couldn't match your input with my knowledge base. Type 'help' for examples.

You: Bye
OrbitBot: Goodbye! It was nice chatting with you. Have a great day!
```

---

## Running the Automated Tests

Execute the test suite covering greetings, identity, dynamic responses, exit commands, fallbacks, and input normalization:

```bash
python -m unittest discover -s rule_based_chatbot -p "test_*.py" -v
```

All 10 unit tests execute in milliseconds with 100% pass rate.
