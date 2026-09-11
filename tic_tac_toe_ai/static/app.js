/**
 * Tic-Tac-Toe AI - Client Game Controller
 * =======================================
 * Manages board state, API calls, SVG animated strike line, Web Audio effects,
 * scoreboard persistence, and difficulty switching.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const cells = document.querySelectorAll('.cell');
  const statusBanner = document.getElementById('status-banner');
  const statusText = document.getElementById('status-text');
  const diffButtons = document.querySelectorAll('.diff-btn');
  const scorePlayerEl = document.getElementById('score-player');
  const scoreAiEl = document.getElementById('score-ai');
  const scoreDrawEl = document.getElementById('score-draw');
  const btnNewGame = document.getElementById('btn-new-game');
  const btnAiFirst = document.getElementById('btn-ai-first');
  const btnSound = document.getElementById('btn-sound');
  const iconSoundOn = document.getElementById('icon-sound-on');
  const iconSoundOff = document.getElementById('icon-sound-off');
  const btnResetScores = document.getElementById('btn-reset-scores');
  const strikeLine = document.getElementById('strike-line');

  // Game State
  let board = Array(9).fill(' ');
  let difficulty = 'hard';
  let isGameOver = false;
  let isAiThinking = false;
  let soundEnabled = localStorage.getItem('ttt_sound') !== 'false';

  // Scores
  let scores = {
    player: parseInt(localStorage.getItem('ttt_score_player') || '0', 10),
    ai: parseInt(localStorage.getItem('ttt_score_ai') || '0', 10),
    draw: parseInt(localStorage.getItem('ttt_score_draw') || '0', 10),
  };

  updateScoreboardDisplay();
  updateSoundIcon();

  // ---------------- Web Audio API Synthesizer ----------------
  function playSound(type) {
    if (!soundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const now = ctx.currentTime;

      if (type === 'x') {
        // High electric chirp
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(720, now + 0.08);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'o') {
        // Deep smooth drop
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(180, now + 0.12);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
      } else if (type === 'win') {
        // 3-note ascending fanfare
        [523.25, 659.25, 783.99].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const t = now + idx * 0.1;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, t);
          gain.gain.setValueAtTime(0.08, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.22);
        });
      } else if (type === 'loss') {
        // 2-note descending tone
        [380, 260].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const t = now + idx * 0.14;
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(freq, t);
          gain.gain.setValueAtTime(0.06, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.25);
        });
      } else if (type === 'draw') {
        // Warm dual tone
        [440, 440].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const t = now + idx * 0.09;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, t);
          gain.gain.setValueAtTime(0.06, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.16);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.16);
        });
      }
    } catch (e) {
      console.warn('Audio synthesis unavailable:', e);
    }
  }

  function updateSoundIcon() {
    if (soundEnabled) {
      iconSoundOn.classList.remove('hidden');
      iconSoundOff.classList.add('hidden');
    } else {
      iconSoundOn.classList.add('hidden');
      iconSoundOff.classList.remove('hidden');
    }
  }

  btnSound.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    localStorage.setItem('ttt_sound', soundEnabled);
    updateSoundIcon();
  });

  // ---------------- Board & Move Rendering ----------------
  function renderCell(index, mark) {
    const cell = cells[index];
    cell.textContent = mark;
    cell.classList.remove('mark-x', 'mark-o', 'occupied');
    if (mark === 'X') {
      cell.classList.add('mark-x', 'occupied');
      cell.disabled = true;
    } else if (mark === 'O') {
      cell.classList.add('mark-o', 'occupied');
      cell.disabled = true;
    } else {
      cell.disabled = false;
    }
  }

  function setStatus(text, state = '') {
    statusText.textContent = text;
    statusBanner.className = 'status-banner';
    if (state) {
      statusBanner.classList.add(`state-${state}`);
    }
  }

  // ---------------- Winning Strike Line SVG ----------------
  // Coordinates mapped to 300x300 SVG viewbox
  const STRIKE_COORDINATES = {
    '0,1,2': { x1: 25, y1: 50, x2: 275, y2: 50 },
    '3,4,5': { x1: 25, y1: 150, x2: 275, y2: 150 },
    '6,7,8': { x1: 25, y1: 250, x2: 275, y2: 250 },
    '0,3,6': { x1: 50, y1: 25, x2: 50, y2: 275 },
    '1,4,7': { x1: 150, y1: 25, x2: 150, y2: 275 },
    '2,5,8': { x1: 250, y1: 25, x2: 250, y2: 275 },
    '0,4,8': { x1: 30, y1: 30, x2: 270, y2: 270 },
    '2,4,6': { x1: 270, y1: 30, x2: 30, y2: 270 },
  };

  function drawStrikeLine(winningLine, winner) {
    if (!winningLine) return;
    const key = winningLine.join(',');
    const coords = STRIKE_COORDINATES[key];
    if (!coords) return;

    strikeLine.setAttribute('x1', coords.x1);
    strikeLine.setAttribute('y1', coords.y1);
    strikeLine.setAttribute('x2', coords.x2);
    strikeLine.setAttribute('y2', coords.y2);

    strikeLine.className = `strike-line line-${winner.toLowerCase()}`;
    strikeLine.classList.remove('hidden');

    winningLine.forEach((idx) => {
      cells[idx].classList.add('winning-cell');
    });
  }

  function clearStrikeLine() {
    strikeLine.classList.add('hidden');
    cells.forEach((cell) => cell.classList.remove('winning-cell'));
  }

  // ---------------- Game Actions & API ----------------
  async function handleCellClick(e) {
    const targetCell = e.target.closest('.cell');
    if (!targetCell) return;

    const idx = parseInt(targetCell.dataset.index, 10);
    if (isNaN(idx) || board[idx] !== ' ' || isGameOver || isAiThinking) {
      return;
    }

    // Immediately render player's mark 'X'
    board[idx] = 'X';
    renderCell(idx, 'X');
    playSound('x');

    isAiThinking = true;
    setStatus('AI is calculating move...', '');

    try {
      // Send move to Flask API
      const res = await fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          board: board,
          player_move: idx,
          difficulty: difficulty,
        }),
      });

      const data = await res.json();
      if (!data.success) {
        setStatus('Error making move. Try again.', '');
        isAiThinking = false;
        return;
      }

      // If player won on this turn
      if (data.status === 'win') {
        board = data.board;
        drawStrikeLine(data.winning_line, 'X');
        setStatus('🎉 You Won! Magnificent play!', 'win');
        scores.player++;
        saveScores();
        playSound('win');
        isGameOver = true;
        isAiThinking = false;
        return;
      }

      // If draw on player move
      if (data.status === 'draw' && data.ai_move === null) {
        board = data.board;
        setStatus("🤝 It's a Draw!", 'draw');
        scores.draw++;
        saveScores();
        playSound('draw');
        isGameOver = true;
        isAiThinking = false;
        return;
      }

      // Add a small natural delay (280ms) for AI move feel
      await new Promise((resolve) => setTimeout(resolve, 280));

      // Render AI Move
      if (data.ai_move !== null && data.ai_move !== undefined) {
        board = data.board;
        renderCell(data.ai_move, 'O');
        playSound('o');
      }

      // Check final state after AI move
      if (data.status === 'loss') {
        drawStrikeLine(data.winning_line, 'O');
        setStatus('🤖 AI Won this round! Try again.', 'loss');
        scores.ai++;
        saveScores();
        playSound('loss');
        isGameOver = true;
      } else if (data.status === 'draw') {
        setStatus("🤝 It's a Draw! Good match.", 'draw');
        scores.draw++;
        saveScores();
        playSound('draw');
        isGameOver = true;
      } else {
        setStatus('Your Turn (X) — Pick a cell', '');
      }
    } catch (err) {
      console.error('Move error:', err);
      setStatus('Network error occurred.', '');
    } finally {
      isAiThinking = false;
    }
  }

  async function letAiStart() {
    if (board.some((c) => c !== ' ') || isAiThinking) {
      resetGame();
    }

    isAiThinking = true;
    setStatus('AI is thinking of an opening move...', '');

    try {
      const res = await fetch('/api/ai-first', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ difficulty: difficulty }),
      });
      const data = await res.json();
      if (data.success && data.ai_move !== undefined) {
        board = data.board;
        renderCell(data.ai_move, 'O');
        playSound('o');
        setStatus('AI made its move. Your Turn (X)!', '');
      }
    } catch (err) {
      console.error('AI-first error:', err);
      setStatus('Could not trigger AI move.', '');
    } finally {
      isAiThinking = false;
    }
  }

  function resetGame() {
    board = Array(9).fill(' ');
    isGameOver = false;
    isAiThinking = false;
    clearStrikeLine();
    cells.forEach((cell, i) => renderCell(i, ' '));
    setStatus('Your Turn (X) — Pick a cell', '');
  }

  // ---------------- Scoreboard Helpers ----------------
  function updateScoreboardDisplay() {
    scorePlayerEl.textContent = scores.player;
    scoreAiEl.textContent = scores.ai;
    scoreDrawEl.textContent = scores.draw;
  }

  function saveScores() {
    updateScoreboardDisplay();
    localStorage.setItem('ttt_score_player', scores.player);
    localStorage.setItem('ttt_score_ai', scores.ai);
    localStorage.setItem('ttt_score_draw', scores.draw);
  }

  btnResetScores.addEventListener('click', () => {
    scores = { player: 0, ai: 0, draw: 0 };
    saveScores();
  });

  // ---------------- Difficulty Switcher ----------------
  diffButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      diffButtons.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      difficulty = btn.dataset.level;
      resetGame();
    });
  });

  // ---------------- Event Listeners ----------------
  cells.forEach((cell) => cell.addEventListener('click', handleCellClick));
  btnNewGame.addEventListener('click', resetGame);
  btnAiFirst.addEventListener('click', letAiStart);
});
