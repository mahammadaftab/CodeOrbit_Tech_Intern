"""
Rule-Based Chatbot
==================
A simple conversational chatbot built in Python that uses predefined rules,
keyword matching, and regular expressions to determine its responses.

Decision Logic Workflow:
-------------------------
1. Receive raw user text.
2. Clean & normalize the input (lowercase, strip whitespace, strip trailing punctuation).
3. Check for exit/quit signals to determine if conversation should terminate.
4. Iterate through ordered rule definitions (patterns & keywords).
   - If a rule's pattern matches or keywords are detected, execute its handler
     or pick from predefined responses.
5. If no predefined rule matches, trigger a graceful fallback response.
"""

import re
import random
from datetime import datetime
from typing import Tuple, List, Dict, Callable, Union


class RuleBasedChatbot:
    """
    A rule-based chatbot that processes user messages through a sequence of
    pattern-matching and keyword-matching rules.
    """

    def __init__(self, name: str = "OrbitBot"):
        self.name = name
        
        # Define the rules dictionary:
        # Each rule contains:
        #   - 'patterns': List of compiled regex patterns to test against normalized input.
        #   - 'responses': List of possible canned string responses (one selected at random),
        #                  OR a callable function that returns a dynamic string.
        #   - 'description': Brief explanation of the rule's intent.
        self.rules: List[Dict[str, Union[List[str], Callable[[], str], str]]] = [
            # 1. GREETING RULE:
            # Matches standard greetings like "hello", "hi", "hey", "good morning", etc.
            {
                "patterns": [
                    r"\b(hello|hi|hey|howdy|hola|greetings)\b",
                    r"\bgood\s+(morning|afternoon|evening)\b",
                    r"\bwhat'?s\s+up\b",
                ],
                "responses": [
                    f"Hello! I'm {self.name}. How can I help you today?",
                    f"Hi there! Good to meet you. What's on your mind?",
                    f"Greetings! How may I assist you today?",
                ],
                "description": "Handles greeting phrases and welcomes the user.",
                "tag": "Greeting",
            },

            # 2. BOT IDENTITY & STATUS RULE:
            # Matches questions regarding the bot's identity, role, or well-being.
            {
                "patterns": [
                    r"\b(who|what)\s+are\s+you\b",
                    r"\bwhat('?s|\s+is)\s+your\s+name\b",
                ],
                "responses": [
                    f"I am {self.name}, a rule-based virtual assistant created to assist you with common questions!",
                    f"My name is {self.name}! I'm a rule-based Python chatbot designed to answer questions based on predefined rules.",
                ],
                "description": "Answers questions about bot identity and name.",
                "tag": "Identity",
            },
            {
                "patterns": [
                    r"\bhow\s+are\s+you\b",
                    r"\bhow('?s|\s+is)\s+it\s+going\b",
                    r"\bhow\s+do\s+you\s+do\b",
                ],
                "responses": [
                    "I'm running smoothly, thank you for asking! How are you doing?",
                    "All systems operational and ready to help! How is your day going?",
                    "I'm doing great! How can I be of service today?",
                ],
                "description": "Responds politely to well-being inquiries.",
                "tag": "Well-being",
            },

            # 3. BOT CAPABILITIES RULE:
            # Answers "what can you do" or "how do you work"
            {
                "patterns": [
                    r"\bwhat\s+can\s+you\s+do\b",
                    r"\bwhat\s+are\s+your\s+capabilities\b",
                    r"\bhow\s+do\s+you\s+work\b",
                ],
                "responses": [
                    "I can chat with you, tell you the current date/time, share a joke, provide help, and answer common questions using predefined rules!",
                    "I process your text using pattern matching and keyword detection to give informative answers or guide you to what you need.",
                ],
                "description": "Explains the chatbot's capabilities and mechanism.",
                "tag": "Capabilities",
            },

            # 4. TIME & DATE DYNAMIC RULES:
            # Generates dynamic responses based on the system's current clock.
            {
                "patterns": [
                    r"\bwhat\s+time\s+is\s+it\b",
                    r"\bcurrent\s+time\b",
                    r"\btell\s+me\s+the\s+time\b",
                ],
                "responses": self._get_current_time,
                "description": "Provides the real-time system clock.",
                "tag": "Time",
            },
            {
                "patterns": [
                    r"\bwhat\s+(is\s+)?today'?s\s+date\b",
                    r"\bwhat\s+is\s+the\s+date\b",
                    r"\bcurrent\s+date\b",
                ],
                "responses": self._get_current_date,
                "description": "Provides the current system date.",
                "tag": "Date",
            },

            # 5. JOKES & ENTERTAINMENT RULE:
            # Fun, lighthearted interaction.
            {
                "patterns": [
                    r"\b(tell\s+me\s+a\s+joke|make\s+me\s+laugh|know\s+any\s+jokes?)\b",
                    r"\bjoke\b",
                ],
                "responses": [
                    "Why do programmers prefer dark mode? Because light attracts bugs!",
                    "Why do Python programmers have low vision? Because they don't C#!",
                    "There are 10 types of people in the world: those who understand binary, and those who don't.",
                    "Why was the JavaScript developer sad? Because they didn't know how to 'null' their feelings!",
                ],
                "description": "Tells a programming or lighthearted joke.",
                "tag": "Joke",
            },

            # 6. GRATITUDE & COMPLIMENTS:
            {
                "patterns": [
                    r"\b(thank\s+you|thanks|thx|appreciate\s+it)\b",
                    r"\b(great|awesome|cool|nice)\s+job\b",
                ],
                "responses": [
                    "You're very welcome! Let me know if there's anything else I can do.",
                    "Happy to help! Feel free to ask if you have more questions.",
                    "Glad I could be of assistance!",
                ],
                "description": "Responds politely to expressions of gratitude.",
                "tag": "Gratitude",
            },

            # 7. HELP / INSTRUCTIONS:
            {
                "patterns": [
                    r"\bhelp\b",
                    r"\bcommands\b",
                    r"\bwhat\s+can\s+i\s+ask\b",
                ],
                "responses": [
                    (
                        "Here are some things you can ask me:\n"
                        "  - Greetings: 'Hello', 'Hi', 'Good morning'\n"
                        "  - Identity: 'Who are you?', 'What is your name?', 'How are you?'\n"
                        "  - Utilities: 'What time is it?', 'What is today\\'s date?'\n"
                        "  - Fun: 'Tell me a joke'\n"
                        "  - Help: 'Help', 'What can you do?'\n"
                        "  - Exit: 'bye', 'exit', 'quit'"
                    ),
                ],
                "description": "Displays available help topics and suggested queries.",
                "tag": "Help",
            },
        ]

        # 8. EXIT / FAREWELL PATTERNS:
        # Used to detect when the conversation should end.
        self.exit_patterns = [
            r"\b(bye|goodbye|cya|see\s+you|farewell)\b",
            r"\b(exit|quit)\b",
        ]

        # 9. FALLBACK RESPONSES:
        # Returned when input does not match any predefined pattern or rule.
        self.fallback_responses = [
            "I'm sorry, I didn't quite understand that. Could you please rephrase?",
            "I'm not sure how to answer that yet. Type 'help' to see what topics I can assist with!",
            "Hmm, that's not something I have a rule for yet. Try asking me for the time, a joke, or type 'help'.",
            "I am a rule-based bot and couldn't match your input with my knowledge base. Type 'help' for examples.",
        ]

    # --- Helper methods for dynamic values ---

    def _get_current_time(self) -> str:
        """Returns formatted current system time."""
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    def _get_current_date(self) -> str:
        """Returns formatted current system date."""
        now = datetime.now()
        return f"Today's date is {now.strftime('%A, %B %d, %Y')}."

    # --- Decision logic & response generation ---

    def normalize_input(self, text: str) -> str:
        """
        Cleans and normalizes user input for robust rule matching:
        - Converts all characters to lowercase.
        - Strips leading and trailing whitespaces.
        - Removes redundant punctuation while preserving alphanumeric characters and spaces.
        """
        text = text.strip().lower()
        # Remove punctuation (e.g., "?", "!", ".") while keeping alphanumeric & spaces
        text = re.sub(r"[^\w\s\']", " ", text)
        # Collapse multiple spaces into a single space
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def is_exit_command(self, normalized_text: str) -> bool:
        """
        Determines whether the user's message is a request to exit or say goodbye.
        
        Decision criteria:
        - Checks the normalized text against exit regex patterns.
        """
        for pattern in self.exit_patterns:
            if re.search(pattern, normalized_text):
                return True
        return False

    def get_detailed_response(self, user_input: str) -> Dict[str, Union[str, bool]]:
        """
        Core decision engine returning rich metadata for both CLI and Web UI.
        
        Returns:
            Dict containing:
                - response: str
                - should_exit: bool
                - matched_rule: str
                - rule_tag: str
                - normalized_text: str
        """
        # Step 1: Validate input
        if not user_input or not user_input.strip():
            return {
                "response": "You didn't say anything! Feel free to ask me something or type 'help'.",
                "should_exit": False,
                "matched_rule": "Empty Input Prompt",
                "rule_tag": "System",
                "normalized_text": "",
            }

        # Step 2: Normalize
        clean_text = self.normalize_input(user_input)

        # Step 3: Check exit command
        if self.is_exit_command(clean_text):
            farewell = random.choice([
                "Goodbye! It was nice chatting with you. Have a great day!",
                "Bye for now! Don't hesitate to reach out if you need anything else.",
                "Farewell! Take care!",
            ])
            return {
                "response": farewell,
                "should_exit": True,
                "matched_rule": "Farewell / Exit Command",
                "rule_tag": "Exit",
                "normalized_text": clean_text,
            }

        # Step 4: Rule pattern evaluation
        for rule in self.rules:
            patterns = rule["patterns"]
            for pattern in patterns:
                if re.search(pattern, clean_text):
                    responses = rule["responses"]
                    if callable(responses):
                        reply = responses()
                    elif isinstance(responses, list):
                        reply = random.choice(responses)
                    else:
                        reply = str(responses)

                    return {
                        "response": reply,
                        "should_exit": False,
                        "matched_rule": rule.get("description", "Pattern Match Rule"),
                        "rule_tag": rule.get("tag", "Matched Rule"),
                        "normalized_text": clean_text,
                    }

        # Step 5: Fallback response when no rules matched
        fallback = random.choice(self.fallback_responses)
        return {
            "response": fallback,
            "should_exit": False,
            "matched_rule": "Default Fallback (Unrecognized input)",
            "rule_tag": "Fallback",
            "normalized_text": clean_text,
        }

    def get_response(self, user_input: str) -> Tuple[str, bool]:
        """
        Maintains backwards compatibility for CLI and automated test suites.
        Returns a (response, should_exit) tuple.
        """
        details = self.get_detailed_response(user_input)
        return str(details["response"]), bool(details["should_exit"])


def run_chat_session():
    """Starts an interactive command-line chat session with the user."""
    bot = RuleBasedChatbot()
    print("=" * 60)
    print(f"       Welcome to {bot.name} - Rule-Based Chatbot")
    print("=" * 60)
    print("Type your message below and press Enter.")
    print("Type 'help' to see what I can do, or 'exit' / 'bye' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            response, should_exit = bot.get_response(user_input)
            print(f"{bot.name}: {response}\n")

            if should_exit:
                break
        except (KeyboardInterrupt, EOFError):
            print(f"\n{bot.name}: Session interrupted. Goodbye!")
            break


if __name__ == "__main__":
    run_chat_session()
