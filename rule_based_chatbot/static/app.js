/**
 * OrbitBot - Web Client Logic
 * ===========================
 * Handles asynchronous chat interactions, typing effects, rule inspector modal,
 * audio chime synthesizers, and dynamic prompt suggestions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const messagesContainer = document.getElementById('messages-container');
  const chatForm = document.getElementById('chat-form');
  const messageInput = document.getElementById('message-input');
  const btnSend = document.getElementById('btn-send');
  const typingIndicator = document.getElementById('typing-indicator');
  const suggestionsBar = document.getElementById('suggestions-bar');
  const btnSoundToggle = document.getElementById('btn-sound-toggle');
  const iconSoundOn = document.getElementById('icon-sound-on');
  const iconSoundOff = document.getElementById('icon-sound-off');
  const btnClearChat = document.getElementById('btn-clear-chat');
  const btnInspectRules = document.getElementById('btn-inspect-rules');
  const modalRules = document.getElementById('modal-rules');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const rulesTableBody = document.getElementById('rules-table-body');
  const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
  const sidebar = document.getElementById('sidebar');

  // State
  let soundEnabled = localStorage.getItem('orbitbot_sound') !== 'false';
  let isSending = false;

  // Initialize Sound Icon
  updateSoundIcon();

  // Load Suggestions and Rules
  loadSuggestions();

  // ---------------- Sound Effects (Web Audio API Synthesizer) ----------------
  function playChime(type) {
    if (!soundEnabled) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      if (type === 'user') {
        // Soft pop for user send
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(660, ctx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.08);
      } else if (type === 'bot') {
        // Gentle pleasant two-tone chime for bot reply
        const now = ctx.currentTime;
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = 'triangle';
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(880, now + 0.08); // A5

        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(ctx.destination);

        osc1.start(now);
        osc1.stop(now + 0.1);
        osc2.start(now + 0.08);
        osc2.stop(now + 0.35);
      }
    } catch (e) {
      console.warn('Audio synthesis not supported or blocked:', e);
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

  btnSoundToggle.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    localStorage.setItem('orbitbot_sound', soundEnabled);
    updateSoundIcon();
  });

  // ---------------- Message Rendering ----------------
  function appendMessage(sender, text, options = {}) {
    const { time = formatCurrentTime(), ruleTag = null, isUser = false } = options;

    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isUser ? 'user-message' : 'bot-message'}`;

    // Avatar
    const avatarCol = document.createElement('div');
    avatarCol.className = 'avatar-col';

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${isUser ? 'user-avatar' : 'bot-avatar'}`;
    if (isUser) {
      avatar.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      `;
    } else {
      avatar.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="8" width="18" height="12" rx="4"/>
          <circle cx="8" cy="13" r="1.5" fill="currentColor"/>
          <circle cx="16" cy="13" r="1.5" fill="currentColor"/>
        </svg>
      `;
    }
    avatarCol.appendChild(avatar);

    // Bubble Column
    const bubbleCol = document.createElement('div');
    bubbleCol.className = 'bubble-col';

    // Header metadata
    const senderRow = document.createElement('div');
    senderRow.className = 'message-sender';

    const nameSpan = document.createElement('span');
    nameSpan.textContent = sender;
    senderRow.appendChild(nameSpan);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = time;
    senderRow.appendChild(timeSpan);

    // Tag badge for bot
    if (!isUser && ruleTag) {
      const tagSpan = document.createElement('span');
      const cleanTag = ruleTag.toLowerCase().replace(/[\s\W]+/g, '-');
      tagSpan.className = `rule-badge tag-${cleanTag}`;
      tagSpan.textContent = ruleTag;
      senderRow.appendChild(tagSpan);
    }
    bubbleCol.appendChild(senderRow);

    // Bubble body
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Format newlines into paragraphs
    const paragraphs = text.split('\n');
    paragraphs.forEach((pText) => {
      if (pText.trim()) {
        const p = document.createElement('p');
        p.textContent = pText;
        bubble.appendChild(p);
      }
    });

    bubbleCol.appendChild(bubble);

    wrapper.appendChild(avatarCol);
    wrapper.appendChild(bubbleCol);

    messagesContainer.appendChild(wrapper);
    scrollToBottom();
  }

  function formatCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    return `${hours}:${minutes} ${ampm}`;
  }

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // ---------------- API Call & Chat Handling ----------------
  async function sendMessage(text) {
    if (!text || !text.trim() || isSending) return;

    const userText = text.trim();
    messageInput.value = '';
    isSending = true;
    btnSend.disabled = true;

    // Render user message immediately
    appendMessage('You', userText, { isUser: true });
    playChime('user');

    // Show typing indicator
    typingIndicator.classList.remove('hidden');
    scrollToBottom();

    try {
      // Simulate realistic evaluation delay (400ms) for pleasant feel
      const [response] = await Promise.all([
        fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userText }),
        }).then((res) => res.json()),
        new Promise((resolve) => setTimeout(resolve, 450)),
      ]);

      typingIndicator.classList.add('hidden');

      if (response && response.success) {
        appendMessage(response.bot_name || 'OrbitBot', response.response, {
          time: response.timestamp,
          ruleTag: response.rule_tag,
          isUser: false,
        });
        playChime('bot');

        // If exit was triggered, disable input with friendly message
        if (response.should_exit) {
          messageInput.placeholder = 'Conversation ended. Click reset to start again.';
        }
      } else {
        appendMessage('OrbitBot', 'Sorry, an unexpected error occurred. Please try again.', {
          ruleTag: 'Error',
        });
      }
    } catch (err) {
      console.error('Chat error:', err);
      typingIndicator.classList.add('hidden');
      appendMessage('OrbitBot', 'Network error. Please make sure the server is running.', {
        ruleTag: 'Error',
      });
    } finally {
      isSending = false;
      btnSend.disabled = false;
      messageInput.focus();
    }
  }

  // ---------------- Event Listeners ----------------
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(messageInput.value);
  });

  // Clear / Reset Chat
  btnClearChat.addEventListener('click', async () => {
    try {
      await fetch('/api/reset', { method: 'POST' });
    } catch (e) {
      // Ignore network errors on reset
    }
    messagesContainer.innerHTML = '';
    appendMessage('OrbitBot', "Conversation reset! What would you like to chat about?", {
      ruleTag: 'Greeting',
    });
    messageInput.placeholder = "Ask OrbitBot something (e.g. 'What time is it?', 'Tell me a joke')...";
  });

  // ---------------- Suggestions Loading ----------------
  async function loadSuggestions() {
    try {
      const res = await fetch('/api/suggestions');
      const data = await res.json();
      if (data && data.success && Array.isArray(data.suggestions)) {
        renderSuggestions(data.suggestions);
      }
    } catch (e) {
      // Fallback default suggestions
      renderSuggestions([
        { label: '👋 Say Hello', text: 'Hello!' },
        { label: '⏰ Current Time', text: 'What time is it?' },
        { label: '📅 Today Date', text: "What is today's date?" },
        { label: '😂 Tell a Joke', text: 'Tell me a joke!' },
        { label: '💡 Help', text: 'help' },
      ]);
    }
  }

  function renderSuggestions(list) {
    suggestionsBar.innerHTML = '';
    list.forEach((item) => {
      const pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'suggestion-pill';
      pill.textContent = item.label;
      pill.addEventListener('click', () => {
        sendMessage(item.text);
      });
      suggestionsBar.appendChild(pill);
    });
  }

  // ---------------- Rule Inspector Modal ----------------
  btnInspectRules.addEventListener('click', async () => {
    modalRules.classList.remove('hidden');
    try {
      const res = await fetch('/api/rules');
      const data = await res.json();
      if (data && data.success) {
        renderRulesTable(data.rules);
      }
    } catch (e) {
      rulesTableBody.innerHTML = '<p class="error">Could not load rules from server.</p>';
    }
  });

  function renderRulesTable(rules) {
    let html = `
      <table class="rules-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Sample Regex Pattern</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
    `;

    rules.forEach((r) => {
      html += `
        <tr>
          <td><strong>${r.tag}</strong></td>
          <td><code class="pattern-code">${escapeHtml(r.sample_pattern)}</code></td>
          <td>${escapeHtml(r.description)}</td>
        </tr>
      `;
    });

    html += `
        <tr>
          <td><strong style="color:#fb7185">Exit</strong></td>
          <td><code class="pattern-code">\\b(bye|goodbye|exit|quit)\\b</code></td>
          <td>Detects parting signals and terminates the session</td>
        </tr>
        <tr>
          <td><strong style="color:#fca5a5">Fallback</strong></td>
          <td><code class="pattern-code">(unmatched)</code></td>
          <td>Triggered when no regular expression matches the input</td>
        </tr>
      </tbody>
    </table>
    `;

    rulesTableBody.innerHTML = html;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  btnCloseModal.addEventListener('click', () => {
    modalRules.classList.add('hidden');
  });

  modalRules.addEventListener('click', (e) => {
    if (e.target === modalRules) {
      modalRules.classList.add('hidden');
    }
  });

  // Mobile sidebar toggle
  if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close sidebar on click outside
    document.addEventListener('click', (e) => {
      if (
        sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !btnToggleSidebar.contains(e.target)
      ) {
        sidebar.classList.remove('open');
      }
    });
  }
});
