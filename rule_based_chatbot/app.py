"""
Flask Web Application for Rule-Based Chatbot
=============================================
Provides a REST API and serves a modern, responsive web user interface
for interacting with OrbitBot.
"""

from datetime import datetime
from flask import Flask, render_template, request, jsonify
from chatbot import RuleBasedChatbot

app = Flask(__name__)
bot = RuleBasedChatbot(name="OrbitBot")

SUGGESTED_PROMPTS = [
    {"label": "👋 Say Hello", "text": "Hello!"},
    {"label": "🤖 Who are you?", "text": "Who are you and what is your name?"},
    {"label": "⏰ What time is it?", "text": "What time is it right now?"},
    {"label": "📅 Today's Date", "text": "What is today's date?"},
    {"label": "😂 Tell a Joke", "text": "Tell me a joke!"},
    {"label": "🛠️ What can you do?", "text": "What can you do?"},
    {"label": "💡 Help", "text": "help"},
    {"label": "❓ Unknown Query", "text": "Can you calculate rocket trajectory?"},
    {"label": "👋 Goodbye", "text": "Goodbye, have a nice day!"},
]


@app.route("/")
def index():
    """Serves the main web chat interface."""
    return render_template("index.html", bot_name=bot.name)


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Processes incoming chat messages via the rule engine.
    Expects JSON: { "message": "user input string" }
    """
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    # Retrieve detailed decision breakdown from chatbot
    result = bot.get_detailed_response(user_message)

    now = datetime.now()
    response_payload = {
        "success": True,
        "bot_name": bot.name,
        "response": result["response"],
        "should_exit": result["should_exit"],
        "matched_rule": result["matched_rule"],
        "rule_tag": result["rule_tag"],
        "normalized_text": result["normalized_text"],
        "timestamp": now.strftime("%I:%M %p"),
    }
    return jsonify(response_payload)


@app.route("/api/suggestions", methods=["GET"])
def suggestions():
    """Returns curated quick-prompt chips for user convenience."""
    return jsonify({"success": True, "suggestions": SUGGESTED_PROMPTS})


@app.route("/api/rules", methods=["GET"])
def get_rules():
    """
    Returns metadata on all configured rules for the 'Rule Inspector'
    panel, providing educational transparency on how rules match.
    """
    rules_info = []
    for r in bot.rules:
        rules_info.append({
            "tag": r.get("tag", "Rule"),
            "description": r.get("description", ""),
            "pattern_count": len(r.get("patterns", [])),
            "sample_pattern": r.get("patterns", [""])[0],
        })

    return jsonify({
        "success": True,
        "bot_name": bot.name,
        "total_rules": len(bot.rules),
        "rules": rules_info,
        "has_exit_rule": True,
        "has_fallback_rule": True,
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    """Resets the conversation state."""
    return jsonify({"success": True, "message": "Session reset successfully."})


if __name__ == "__main__":
    # Start local Flask development server
    print(f"Starting {bot.name} Web Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
