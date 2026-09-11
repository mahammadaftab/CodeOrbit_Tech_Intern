"""
Unit tests for Tic-Tac-Toe Game Engine and AI Opponents
"""

import unittest
import random
from game import TicTacToe, WINNING_COMBINATIONS


class TestTicTacToeGame(unittest.TestCase):
    def setUp(self):
        self.game = TicTacToe()

    def test_initial_board(self):
        """Test board initialization and available moves."""
        self.assertEqual(len(self.game.board), 9)
        self.assertEqual(self.game.board.count(" "), 9)
        self.assertEqual(len(self.game.get_available_moves()), 9)
        self.assertFalse(self.game.is_game_over())

    def test_make_move_validity(self):
        """Test placing valid and invalid moves."""
        # Valid move
        self.assertTrue(self.game.make_move(0, "X"))
        self.assertEqual(self.game.board[0], "X")
        self.assertNotIn(0, self.game.get_available_moves())

        # Invalid move (already occupied)
        self.assertFalse(self.game.make_move(0, "O"))
        self.assertEqual(self.game.board[0], "X")

        # Invalid move (out of bounds)
        self.assertFalse(self.game.make_move(-1, "X"))
        self.assertFalse(self.game.make_move(9, "X"))

    def test_all_winning_combinations(self):
        """Test that all 8 winning combinations are accurately detected."""
        for combo in WINNING_COMBINATIONS:
            with self.subTest(combo=combo):
                test_board = [" "] * 9
                for idx in combo:
                    test_board[idx] = "X"

                winner, line = self.game.check_winner(test_board)
                self.assertEqual(winner, "X")
                self.assertEqual(line, combo)
                self.assertTrue(self.game.is_game_over(test_board))

    def test_draw_condition(self):
        """Test full board with no winner results in a draw."""
        # Known draw board:
        # X | O | X
        # X | O | O
        # O | X | X
        draw_board = [
            "X", "O", "X",
            "X", "O", "O",
            "O", "X", "X"
        ]
        winner, line = self.game.check_winner(draw_board)
        self.assertIsNone(winner)
        self.assertIsNone(line)
        self.assertTrue(self.game.is_draw(draw_board))
        self.assertTrue(self.game.is_game_over(draw_board))

    def test_rule_based_ai_winning_move(self):
        """Medium AI must take an immediate winning move if available."""
        # AI ("O") has positions 0 and 1, position 2 is free
        # O | O | _
        # X | X | _
        # _ | _ | _
        board = [
            "O", "O", " ",
            "X", "X", " ",
            " ", " ", " "
        ]
        ai_move = self.game.get_ai_move(difficulty="medium", board=board)
        self.assertEqual(ai_move, 2, f"Expected AI to take winning position 2, got {ai_move}")

    def test_rule_based_ai_block_move(self):
        """Medium AI must block Human player ("X") if they have 2 in a row."""
        # Human ("X") has positions 3 and 4, position 5 is free
        # O | _ | _
        # X | X | _
        # _ | _ | _
        board = [
            "O", " ", " ",
            "X", "X", " ",
            " ", " ", " "
        ]
        ai_move = self.game.get_ai_move(difficulty="medium", board=board)
        self.assertEqual(ai_move, 5, f"Expected AI to block position 5, got {ai_move}")

    def test_minimax_ai_immediate_win(self):
        """Minimax AI must choose winning move immediately."""
        board = [
            "O", "O", " ",
            "X", "X", " ",
            " ", " ", " "
        ]
        ai_move = self.game.get_ai_move(difficulty="hard", board=board)
        self.assertEqual(ai_move, 2)

    def test_minimax_ai_immediate_block(self):
        """Minimax AI must block human win."""
        board = [
            "X", "X", " ",
            "O", " ", " ",
            " ", " ", " "
        ]
        ai_move = self.game.get_ai_move(difficulty="hard", board=board)
        self.assertEqual(ai_move, 2)

    def test_minimax_never_loses_simulation(self):
        """
        Simulate 30 games against random moves and verify Minimax NEVER loses.
        Result must be either an AI win or a Draw.
        """
        for _ in range(30):
            board = [" "] * 9
            human_turn = random.choice([True, False])

            while not self.game.is_game_over(board):
                if human_turn:
                    # Random human move
                    available = self.game.get_available_moves(board)
                    board[random.choice(available)] = self.game.human
                    human_turn = False
                else:
                    # Optimal Minimax AI move
                    ai_move = self.game.get_ai_move(difficulty="hard", board=board)
                    board[ai_move] = self.game.ai
                    human_turn = True

            winner, _ = self.game.check_winner(board)
            self.assertNotEqual(
                winner,
                self.game.human,
                f"Minimax lost a match! Board state: {board}"
            )


if __name__ == "__main__":
    unittest.main()
