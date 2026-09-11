# Tic-Tac-Toe with AI (Rule-Based & Minimax)

An interactive Tic-Tac-Toe game featuring both a **clear terminal CLI interface** and a **modern, animated web application**. Play against an intelligent computer opponent with three configurable difficulty levels: **Easy**, **Medium (Rule-Based Heuristic)**, and **Hard (Unbeatable Minimax Algorithm)**.

---

## Features

- **Multi-Tier AI Opponent**:
  - **Easy (Casual)**: Plays randomly without checking for winning alignments.
  - **Medium (Rule-Based Heuristics)**: Follows tactical decision rules (takes winning moves, blocks opponent wins, prioritizes center and corner control).
  - **Hard (Optimal Minimax)**: Complete game-tree search using alpha-beta pruning. Evaluates all possible future board states; mathematically impossible to defeat (optimal play guarantees at worst a draw).
- **Clear Board Representation**:
  - **Terminal (CLI)**: Visually distinct grid using Unicode box drawing characters (`━`, `┃`, `╋`), with positions 1–9 clearly indicated for intuitive input.
  - **Web Application**: Glowing neon dark theme (`X` in Electric Cyan, `O` in Neon Magenta), pop-in mark animations, and dynamic SVG winning strike lines.
- **Accurate Condition Detection**:
  - Checks all 8 winning lines (3 horizontal rows, 3 vertical columns, 2 diagonals).
  - Full board draw detection.
  - Real-time score tracking (Wins, Losses, Draws).
- **Interactive Web App**:
  - Real-time move exchange via REST API.
  - Web Audio API synthesized sound effects for placement, victory fanfares, and ties.
  - "Let AI Start First" option.
  - Reset board and reset scoreboard controls.

---

## How the AI Decides Its Moves

### 1. Rule-Based AI (Medium Difficulty)
Evaluates the board through a prioritized heuristic sequence:
1. **Immediate Win**: If the AI has two marks in any row, column, or diagonal, it immediately places its mark in the third cell to claim victory.
2. **Immediate Block**: If the Human player has two marks in any line, the AI detects the threat and blocks that third cell.
3. **Center Control**: Takes the center cell (position 5 / index 4) if open, as it participates in 4 of the 8 possible winning lines.
4. **Corner Control**: Chooses an available corner cell (positions 1, 3, 7, 9 / indices 0, 2, 6, 8).
5. **Edge Control**: Plays any remaining edge cell (positions 2, 4, 6, 8 / indices 1, 3, 5, 7).

### 2. Minimax Algorithm (Hard Difficulty)
The Minimax algorithm explores the complete game decision tree recursively:
- **Terminal State Evaluation**:
  $$\text{Score} = \begin{cases} +10 - \text{depth} & \text{if AI wins (favors faster wins)} \\ -10 + \text{depth} & \text{if Human wins (favors slower losses)} \\ 0 & \text{if Draw} \end{cases}$$
- **Alpha-Beta Pruning**: Prunes branches that cannot influence the final decision to ensure instant calculation.
- **Outcome**: The AI anticipates all future counter-moves. If the user plays sub-optimally, the AI wins; if the user plays perfectly, the game terminates in a draw.

---

## Project Structure

```
tic_tac_toe_ai/
├── game.py           # Core board engine, rule-based heuristics, Minimax & CLI loop
├── test_game.py      # Automated unit test suite (win/loss/draw, AI optimality)
├── app.py            # Flask REST API server & web app runner
├── templates/
│   └── index.html    # Accessible, responsive HTML5 game interface
├── static/
│   ├── style.css     # Pure Vanilla CSS design system (neon dark mode & SVG animations)
│   └── app.js        # Client controller (move handling, audio effects, SVG strike line)
└── README.md         # Documentation and execution guide
```

---

## Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.
- Flask (installed or run `pip install flask`).

---

### Option 1: Running the Web Application (Recommended)

1. Start the Flask server:
   ```bash
   python tic_tac_toe_ai/app.py
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5001
   ```
3. Choose your difficulty, click cells to play, or click "Let AI Start First"!

---

### Option 2: Running the Terminal Game (CLI)

Run the standalone interactive command-line match:
```bash
python tic_tac_toe_ai/game.py
```

#### Sample Terminal Interaction
```text
=======================================================
        WELCOME TO TIC-TAC-TOE WITH AI
=======================================================
Play against the computer on a 3x3 grid.
Cells are numbered 1 through 9 as shown below:

   1 ┃ 2 ┃ 3 
  ━━━╋━━━╋━━━
   4 ┃ 5 ┃ 6 
  ━━━╋━━━╋━━━
   7 ┃ 8 ┃ 9 

Choose AI Difficulty Level:
  [1] Easy   - Plays casually and makes mistakes
  [2] Medium - Rule-based (blocks wins, takes center/corners)
  [3] Hard   - Unbeatable Minimax algorithm (optimal play)
Enter difficulty (1/2/3, default=3): 3

AI Difficulty set to: HARD
----------------------------------------
Current Score: You (X): 0 | AI (O): 0 | Draws: 0
----------------------------------------
Do you want to go first as X? (y/n, default=y): y

Your turn (Choose position 1-9, or 'q' to quit): 1

You placed an 'X':

   X ┃ 2 ┃ 3 
  ━━━╋━━━╋━━━
   4 ┃ 5 ┃ 6 
  ━━━╋━━━╋━━━
   7 ┃ 8 ┃ 9 

Computer (O) is thinking...

Computer placed an 'O' at position 5:

   X ┃ 2 ┃ 3 
  ━━━╋━━━╋━━━
   4 ┃ O ┃ 6 
  ━━━╋━━━╋━━━
   7 ┃ 8 ┃ 9 
```

---

## Running the Automated Tests

Execute the unit test suite with Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tic_tac_toe_ai -p "test_*.py" -v
```

### Verified Test Cases:
- Board initialization and available moves tracking.
- Move legality and bounds checking.
- All 8 winning lines detection (rows, columns, diagonals).
- Draw condition evaluation on a full board without a winner.
- Rule-based AI immediate win execution.
- Rule-based AI immediate opponent block execution.
- Minimax immediate win and block execution.
- 30-game randomized Monte Carlo simulation verifying Minimax never loses.
