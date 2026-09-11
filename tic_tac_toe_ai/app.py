"""
Flask Web Application for Tic-Tac-Toe AI
=========================================
Exposes a REST API for moves and game state evaluation, serving a modern,
responsive, and animated web UI.
"""

from flask import Flask, render_template, request, jsonify
from game import TicTacToe

app = Flask(__name__)
engine = TicTacToe()


@app.route("/")
def index():
    """Serves the main Tic-Tac-Toe web interface."""
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    """Handle browser favicon request to avoid 404."""
    return ("", 204)


@app.route("/api/move", methods=["POST"])
def player_move():
    """
    Handles a player's move, checks game state, and triggers AI response.
    Expects JSON:
    {
        "board": List[str],            # 9-element list of ' ', 'X', 'O'
        "player_move": int,            # 0-8 index of player move
        "difficulty": str              # 'easy', 'medium', or 'hard'
    }
    """
    data = request.get_json(silent=True) or {}
    board = data.get("board", [" "] * 9)
    player_idx = data.get("player_move")
    difficulty = data.get("difficulty", "hard").lower()

    if not isinstance(board, list) or len(board) != 9:
        return jsonify({"success": False, "error": "Invalid board format"}), 400

    # Step 1: Validate and execute player's move
    if player_idx is not None:
        if not (0 <= player_idx < 9):
            return jsonify({"success": False, "error": "Move index out of bounds"}), 400
        # If square is occupied by AI mark, it's an illegal override
        if board[player_idx] == engine.ai:
            return jsonify({"success": False, "error": "Square already taken by AI"}), 400
        # Place human mark
        board[player_idx] = engine.human

    # Step 2: Check if player won or board is full
    winner, winning_line = engine.check_winner(board)
    if winner == engine.human:
        return jsonify({
            "success": True,
            "board": board,
            "player_move": player_idx,
            "ai_move": None,
            "winner": engine.human,
            "winning_line": winning_line,
            "is_draw": False,
            "status": "win",
        })

    if engine.is_draw(board):
        return jsonify({
            "success": True,
            "board": board,
            "player_move": player_idx,
            "ai_move": None,
            "winner": None,
            "winning_line": None,
            "is_draw": True,
            "status": "draw",
        })

    # Step 3: Compute AI move
    ai_idx = engine.get_ai_move(difficulty=difficulty, board=board)
    if ai_idx != -1:
        board[ai_idx] = engine.ai

    # Step 4: Check if AI won or game resulted in draw
    winner, winning_line = engine.check_winner(board)
    if winner == engine.ai:
        return jsonify({
            "success": True,
            "board": board,
            "player_move": player_idx,
            "ai_move": ai_idx,
            "winner": engine.ai,
            "winning_line": winning_line,
            "is_draw": False,
            "status": "loss",
        })

    if engine.is_draw(board):
        return jsonify({
            "success": True,
            "board": board,
            "player_move": player_idx,
            "ai_move": ai_idx,
            "winner": None,
            "winning_line": None,
            "is_draw": True,
            "status": "draw",
        })

    # Game ongoing
    return jsonify({
        "success": True,
        "board": board,
        "player_move": player_idx,
        "ai_move": ai_idx,
        "winner": None,
        "winning_line": None,
        "is_draw": False,
        "status": "ongoing",
    })


@app.route("/api/ai-first", methods=["POST"])
def ai_first_move():
    """
    Called when player elects the AI to make the first move.
    """
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "hard").lower()
    board = [" "] * 9

    ai_idx = engine.get_ai_move(difficulty=difficulty, board=board)
    board[ai_idx] = engine.ai

    return jsonify({
        "success": True,
        "board": board,
        "ai_move": ai_idx,
        "status": "ongoing",
    })


@app.route("/api/info", methods=["GET"])
def info():
    """Returns AI algorithm descriptions for UI educational tooltips."""
    return jsonify({
        "success": True,
        "difficulties": {
            "easy": "Random Moves — Plays casually without analyzing board state.",
            "medium": "Rule-Based Heuristic — Prioritizes winning moves, blocks opponent wins, and controls center/corners.",
            "hard": "Optimal Minimax — Complete game-tree search with alpha-beta pruning. Mathematically unbeatable."
        }
    })


if __name__ == "__main__":
    # Start local Flask development server on port 5001
    print("Starting Tic-Tac-Toe AI Web Server on http://127.0.0.1:5001 ...")
    app.run(host="127.0.0.1", port=5001, debug=True)
