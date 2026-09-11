"""
Unit tests for RuleBasedChatbot
"""

import unittest
from datetime import datetime
from chatbot import RuleBasedChatbot


class TestRuleBasedChatbot(unittest.TestCase):
    def setUp(self):
        self.bot = RuleBasedChatbot(name="TestBot")

    def test_empty_input(self):
        """Test how the bot handles empty or whitespace-only inputs."""
        response, should_exit = self.bot.get_response("")
        self.assertFalse(should_exit)
        self.assertIn("didn't say anything", response)

        response, should_exit = self.bot.get_response("    ")
        self.assertFalse(should_exit)
        self.assertIn("didn't say anything", response)

    def test_greetings(self):
        """Test various greeting phrases and punctuation combinations."""
        test_inputs = ["hello", "Hi", "HEY!", "Good morning", "howdy there", "greetings"]
        for greeting in test_inputs:
            with self.subTest(greeting=greeting):
                response, should_exit = self.bot.get_response(greeting)
                self.assertFalse(should_exit)
                # Responses should contain a greeting keyword or the bot name
                self.assertTrue(
                    any(word in response.lower() for word in ["hello", "hi", "greetings", "testbot"]),
                    f"Unexpected response for '{greeting}': {response}"
                )

    def test_identity_and_status(self):
        """Test questions about bot's name, role, and well-being."""
        # Name
        response, should_exit = self.bot.get_response("Who are you?")
        self.assertFalse(should_exit)
        self.assertIn("TestBot", response)

        response, should_exit = self.bot.get_response("What is your name?")
        self.assertFalse(should_exit)
        self.assertIn("TestBot", response)

        # Well-being
        response, should_exit = self.bot.get_response("How are you doing today?")
        self.assertFalse(should_exit)
        self.assertTrue(
            any(phrase in response.lower() for phrase in ["smoothly", "operational", "doing great"]),
            f"Unexpected response for 'how are you': {response}"
        )

    def test_capabilities_and_help(self):
        """Test help and capability prompts."""
        response, should_exit = self.bot.get_response("What can you do?")
        self.assertFalse(should_exit)
        self.assertTrue(
            "chat" in response.lower() or "pattern matching" in response.lower(),
            f"Unexpected response: {response}"
        )

        response, should_exit = self.bot.get_response("help")
        self.assertFalse(should_exit)
        self.assertIn("Greetings:", response)
        self.assertIn("Utilities:", response)

    def test_dynamic_time_and_date(self):
        """Test dynamic time and date retrieval."""
        now = datetime.now()

        # Time check
        response, should_exit = self.bot.get_response("What time is it right now?")
        self.assertFalse(should_exit)
        self.assertIn("current time is", response.lower())

        # Date check
        response, should_exit = self.bot.get_response("What is today's date?")
        self.assertFalse(should_exit)
        current_year = str(now.year)
        self.assertIn(current_year, response)

    def test_entertainment_and_jokes(self):
        """Test joke inquiries."""
        response, should_exit = self.bot.get_response("Tell me a joke!")
        self.assertFalse(should_exit)
        self.assertTrue(len(response) > 10)

    def test_gratitude(self):
        """Test gratitude recognition."""
        response, should_exit = self.bot.get_response("Thank you so much!")
        self.assertFalse(should_exit)
        self.assertTrue(
            any(phrase in response.lower() for phrase in ["welcome", "happy to help", "assistance"]),
            f"Unexpected response: {response}"
        )

    def test_exit_commands(self):
        """Test conversational exit and quit signals."""
        exit_phrases = ["bye", "goodbye", "exit", "quit", "see you later"]
        for phrase in exit_phrases:
            with self.subTest(phrase=phrase):
                response, should_exit = self.bot.get_response(phrase)
                self.assertTrue(should_exit, f"Expected should_exit=True for '{phrase}'")
                self.assertTrue(
                    any(word in response.lower() for word in ["goodbye", "bye", "farewell"]),
                    f"Unexpected exit response: {response}"
                )

    def test_fallback_unknown_inputs(self):
        """Test that unrecognized input triggers a proper fallback response."""
        unrecognized_inputs = [
            "qwertyuiopasdfghjkl",
            "explain quantum entanglement in detail",
            "what is 42 multiplied by 987?",
            "xyz123randomquery",
        ]
        for query in unrecognized_inputs:
            with self.subTest(query=query):
                response, should_exit = self.bot.get_response(query)
                self.assertFalse(should_exit)
                self.assertIn(response, self.bot.fallback_responses)

    def test_normalization(self):
        """Test input normalization with erratic spacing and punctuation."""
        clean = self.bot.normalize_input("  HELLO,   WORLD?!  ")
        self.assertEqual(clean, "hello world")


if __name__ == "__main__":
    unittest.main()
