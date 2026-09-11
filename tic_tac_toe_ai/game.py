"""
Tic-Tac-Toe Game Engine with AI
===============================
Provides game board representation, win/loss/draw evaluation, and AI opponents
ranging from simple rule-based heuristics to the optimal Minimax algorithm.
"""

import math
import random
from typing import List, Optional, Tuple, Dict, Any

# Winning 3-in-a-row index triplets on a 0-indexed 3x3 board:
#  0 | 1 | 2
# -----------
#  3 | 4 | 5
# -----------
#  6 | 7 | 8
WINNING_COMBINATIONS = [
    [0, 1, 2],  # Row 1
    [3, 4, 5],  # Row 2
    [6, 7, 8],  # Row 3
    [0, 3, 6],  # Column 1
    [1, 4, 7],  # Column 2
    [2, 5, 8],  # Column 3
    [0, 4, 8],  # Diagonal top-left to bottom-right
    [2, 4, 6],  # Diagonal top-right to bottom-left
]


class TicTacToe:
    """
    Manages the board state and game mechanics for a 3x3 Tic-Tac-Toe match.
    """

    def __init__(self):
        # 9-element list initialized to empty spaces ' '
        self.board: List[str] = [" "] * 9
        self.human: str = "X"
        self.ai: str = "O"

    def reset(self):
        """Resets the board for a new match."""
        self.board = [" "] * 9

    def get_available_moves(self, board: Optional[List[str]] = None) -> List[int]:
        """Returns list of 0-based indices that are still unplayed."""
        b = board if board is not None else self.board
        return [i for i, cell in enumerate(b) if cell == " "]

    def make_move(self, index: int, player: str, board: Optional[List[str]] = None) -> bool:
        """
        Places a player's mark on the board if the cell is available.
        Returns True if successful, False otherwise.
        """
        b = board if board is not None else self.board
        if 0 <= index < 9 and b[index] == " ":
            b[index] = player
            return True
        return False

    def check_winner(self, board: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[List[int]]]:
        """
        Checks if either player has won the game.
        Returns:
            Tuple[Optional[str], Optional[List[int]]]: (winning_player, winning_line)
            e.g. ('X', [0, 1, 2]) or (None, None) if no winner yet.
        """
        b = board if board is not None else self.board
        for combo in WINNING_COMBINATIONS:
            p1, p2, p3 = combo
            if b[p1] != " " and b[p1] == b[p2] == b[p3]:
                return b[p1], combo
        return None, None

    def is_draw(self, board: Optional[List[str]] = None) -> bool:
        """Returns True if all cells are filled and there is no winner."""
        b = board if board is not None else self.board
        winner, _ = self.check_winner(b)
        return winner is None and " " not in b

    def is_game_over(self, board: Optional[List[str]] = None) -> bool:
        """Returns True if someone has won or the board is completely full."""
        b = board if board is not None else self.board
        winner, _ = self.check_winner(b)
        return winner is not None or " " not in b

    # ---------------- AI Implementations ----------------

    def get_ai_move(self, difficulty: str = "hard", board: Optional[List[str]] = None) -> int:
        """
        Dispatches to the appropriate AI algorithm based on selected difficulty:
        - 'easy': Random moves.
        - 'medium': Rule-based heuristic (Win, Block, Center, Corner, Edge).
        - 'hard': Optimal Minimax algorithm (Unbeatable).
        """
        diff = difficulty.lower()
        if diff == "easy":
            return self._get_easy_move(board)
        elif diff == "medium":
            return self._get_rule_based_move(board)
        else:
            # Default to unbeatable Minimax
            return self._get_minimax_move(board)

    def _get_easy_move(self, board: Optional[List[str]] = None) -> int:
        """Easy AI: Chooses randomly among any available square."""
        moves = self.get_available_moves(board)
        if not moves:
            return -1
        return random.choice(moves)

    def _get_rule_based_move(self, board: Optional[List[str]] = None) -> int:
        """
        Rule-Based / Heuristic AI Decision Hierarchy:
        ----------------------------------------------
        Rule 1: Immediate Win - If AI has 2 in a line, take the 3rd to win.
        Rule 2: Immediate Block - If Human has 2 in a line, block that square.
        Rule 3: Center Control - Take the middle square (index 4) if free.
        Rule 4: Corner Control - Take any opposite or available corner (0, 2, 6, 8).
        Rule 5: Edge Control - Take any available side edge (1, 3, 5, 7).
        """
        b = list(board if board is not None else self.board)
        available = self.get_available_moves(b)
        if not available:
            return -1

        # Rule 1: Check if AI can win in this move
        for move in available:
            b[move] = self.ai
            winner, _ = self.check_winner(b)
            b[move] = " "  # Undo
            if winner == self.ai:
                return move

        # Rule 2: Check if Human can win in their next move, and block it
        for move in available:
            b[move] = self.human
            winner, _ = self.check_winner(b)
            b[move] = " "  # Undo
            if winner == self.human:
                return move

        # Rule 3: Take Center (index 4)
        if 4 in available:
            return 4

        # Rule 4: Take Corners
        corners = [c for c in [0, 2, 6, 8] if c in available]
        if corners:
            return random.choice(corners)

        # Rule 5: Take Edges
        edges = [e for e in [1, 3, 5, 7] if e in available]
        if edges:
            return random.choice(edges)

        return available[0]

    def _get_minimax_move(self, board: Optional[List[str]] = None) -> int:
        """
        Minimax Algorithm:
        ------------------
        Explores all game branches recursively.
        Evaluates terminal states:
          - AI win = +10 - depth (favors faster wins)
          - Human win = -10 + depth (favors slower losses if inevitable)
          - Draw = 0
        Guarantees that the AI will NEVER lose if played optimally.
        """
        b = list(board if board is not None else self.board)
        available = self.get_available_moves(b)
        if not available:
            return -1

        # Optimization: On empty board, taking center or corner is always optimal
        if len(available) == 9:
            return 4  # Center is strongest opening move

        best_score = -math.inf
        best_move = available[0]

        for move in available:
            b[move] = self.ai
            score = self._minimax(b, depth=0, is_maximizing=False, alpha=-math.inf, beta=math.inf)
            b[move] = " "  # Undo
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(
        self,
        board: List[str],
        depth: int,
        is_maximizing: bool,
        alpha: float,
        beta: float,
    ) -> int:
        """
        Recursive Minimax function with Alpha-Beta pruning for fast computation.
        """
        winner, _ = self.check_winner(board)
        if winner == self.ai:
            return 10 - depth
        elif winner == self.human:
            return depth - 10
        elif " " not in board:
            return 0

        available = [i for i, cell in enumerate(board) if cell == " "]

        if is_maximizing:
            max_eval = -math.inf
            for move in available:
                board[move] = self.ai
                evaluation = self._minimax(board, depth + 1, False, alpha, beta)
                board[move] = " "  # Undo
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in available:
                board[move] = self.human
                evaluation = self._minimax(board, depth + 1, True, alpha, beta)
                board[move] = " "  # Undo
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval

    # ---------------- Board Display Formatting (CLI) ----------------

    def render_board_cli(self, board: Optional[List[str]] = None) -> str:
        """
        Formats a clean, visually clear representation of the board for terminal play,
        displaying numbered reference positions for empty spaces.
        """
        b = board if board is not None else self.board
        
        # Display cell mark, or its 1-indexed number if empty
        cells = [b[i] if b[i] != " " else str(i + 1) for i in range(9)]
        
        lines = [
            "\n",
            f"   {cells[0]} ┃ {cells[1]} ┃ {cells[2]} ",
            "  ━━━╋━━━╋━━━",
            f"   {cells[3]} ┃ {cells[4]} ┃ {cells[5]} ",
            "  ━━━╋━━━╋━━━",
            f"   {cells[6]} ┃ {cells[7]} ┃ {cells[8]} ",
            "\n"
        ]
        return "\n".join(lines)


# ---------------- Interactive Terminal Session ----------------

def run_cli_game():
    """Starts an interactive command-line match with score tracking."""
    game = TicTacToe()
    scores = {"Human": 0, "AI": 0, "Draws": 0}

    print("=" * 55)
    print("        WELCOME TO TIC-TAC-TOE WITH AI")
    print("=" * 55)
    print("Play against the computer on a 3x3 grid.")
    print("Cells are numbered 1 through 9 as shown below:")
    print(game.render_board_cli())

    # Select difficulty
    print("Choose AI Difficulty Level:")
    print("  [1] Easy   - Plays casually and makes mistakes")
    print("  [2] Medium - Rule-based (blocks wins, takes center/corners)")
    print("  [3] Hard   - Unbeatable Minimax algorithm (optimal play)")
    
    diff_choice = input("Enter difficulty (1/2/3, default=3): ").strip()
    diff_map = {"1": "easy", "2": "medium", "3": "hard"}
    difficulty = diff_map.get(diff_choice, "hard")
    print(f"\nAI Difficulty set to: {difficulty.upper()}")

    while True:
        game.reset()
        print("\n" + "-" * 40)
        print(f"Current Score: You (X): {scores['Human']} | AI (O): {scores['AI']} | Draws: {scores['Draws']}")
        print("-" * 40)

        # Decide who goes first
        first_prompt = input("Do you want to go first as X? (y/n, default=y): ").strip().lower()
        human_turn = first_prompt != "n"

        print("\nMatch started!")
        print(game.render_board_cli())

        while not game.is_game_over():
            if human_turn:
                # Human Player Move
                valid_move = False
                while not valid_move:
                    try:
                        raw = input("Your turn (Choose position 1-9, or 'q' to quit): ").strip()
                        if raw.lower() in ("q", "quit", "exit"):
                            print("\nThanks for playing! Final Score:")
                            print(f"You: {scores['Human']} | AI: {scores['AI']} | Draws: {scores['Draws']}")
                            return

                        pos = int(raw) - 1
                        if pos not in range(9):
                            print("Invalid input! Please choose a number from 1 to 9.")
                            continue
                        if not game.make_move(pos, game.human):
                            print(f"Square {pos + 1} is already occupied! Choose another.")
                            continue
                        valid_move = True
                    except ValueError:
                        print("Please enter a valid number (1-9).")

                print("\nYou placed an 'X':")
                print(game.render_board_cli())
                human_turn = False
            else:
                # Computer AI Move
                print(f"Computer ({game.ai}) is thinking...")
                ai_idx = game.get_ai_move(difficulty=difficulty)
                game.make_move(ai_idx, game.ai)
                print(f"\nComputer placed an '{game.ai}' at position {ai_idx + 1}:")
                print(game.render_board_cli())
                human_turn = True

        # Check outcome
        winner, line = game.check_winner()
        if winner == game.human:
            print("🎉 CONGRATULATIONS! You won the match!")
            scores["Human"] += 1
        elif winner == game.ai:
            print("🤖 GAME OVER! The AI won this round!")
            scores["AI"] += 1
        else:
            print("🤝 IT'S A DRAW! Well played!")
            scores["Draws"] += 1

        # Replay prompt
        play_again = input("\nWould you like to play another round? (y/n, default=y): ").strip().lower()
        if play_again == "n":
            print("\nThanks for playing Tic-Tac-Toe!")
            print(f"Final Score: You: {scores['Human']} | AI: {scores['AI']} | Draws: {scores['Draws']}")
            break


if __name__ == "__main__":
    run_cli_game()
