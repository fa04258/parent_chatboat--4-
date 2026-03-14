/* ═══════════════════════════════════════════════
   Parent Academic Portal – chat.js
   Handles both the login flow and the chat UI
   ═══════════════════════════════════════════════ */

// ── Detect which page we're on ───────────────────
const IS_LOGIN = document.querySelector('.login-card') !== null;
const IS_CHAT  = document.querySelector('.chat-main')  !== null;

/* ══════════════════════════════════════════════════
   LOGIN FLOW
   ══════════════════════════════════════════════════ */
if (IS_LOGIN) {

  function showLoading(on) {
    document.getElementById('loading').classList.toggle('active', on);
  }

  function setError(step, msg) {
    document.getElementById('err-' + step).textContent = msg;
  }

  function goToPanel(num) {
    document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('panel-' + num).classList.add('active');
    // Update step dots
    for (let i = 1; i <= 3; i++) {
      const dot = document.getElementById('step-dot-' + i);
      dot.classList.remove('active', 'done');
      if (i < num)  dot.classList.add('done');
      if (i === num) dot.classList.add('active');
    }
  }

  function goBack(toStep) { goToPanel(toStep); }

  async function verifyRegistration() {
    setError(1, '');
    const val = document.getElementById('reg_number').value.trim();
    if (!val) { setError(1, 'Please enter the registration number.'); return; }

    showLoading(true);
    try {
      const res = await fetch('/verify-registration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reg_number: val }),
      });
      const data = await res.json();
      showLoading(false);
      if (data.success) {
        await _loadContacts();   // fetch & render masked phone buttons
        goToPanel(2);
      } else {
        setError(1, data.message || 'Verification failed.');
      }
    } catch (e) {
      showLoading(false);
      setError(1, 'Network error. Please try again.');
    }
  }

  let _selectedContactIndex = null;  // index of button chosen by user

  async function verifyPhone() {
    setError(2, '');

    let body;
    if (_selectedContactIndex !== null) {
      // User clicked one of the registered-number buttons
      body = { contact_index: _selectedContactIndex };
    } else {
      // User typed a number manually
      const val = document.getElementById('phone').value.trim();
      if (!val) { setError(2, 'Please select a number above or enter your mobile number.'); return; }
      if (!/^\d{10,15}$/.test(val)) { setError(2, 'Enter a valid 10-digit mobile number.'); return; }
      body = { phone: val };
    }

    showLoading(true);
    try {
      const res = await fetch('/verify-phone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      showLoading(false);
      if (data.success) {
        goToPanel(3);
      } else {
        setError(2, data.message || 'Phone verification failed.');
      }
    } catch (e) {
      showLoading(false);
      setError(2, 'Network error. Please try again.');
    }
  }

  async function verifyOTP() {
    setError(3, '');
    const val = document.getElementById('otp').value.trim();
    if (!val) { setError(3, 'Please enter the OTP.'); return; }
    if (!/^\d{6}$/.test(val)) { setError(3, 'OTP must be exactly 6 digits.'); return; }

    showLoading(true);
    try {
      const res = await fetch('/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ otp: val }),
      });
      const data = await res.json();
      showLoading(false);
      if (data.success) {
        window.location.href = data.redirect || '/chat';
      } else {
        setError(3, data.message || 'OTP verification failed.');
      }
    } catch (e) {
      showLoading(false);
      setError(3, 'Network error. Please try again.');
    }
  }

  // ── Contact phone picker ─────────────────────────────
  async function _loadContacts() {
    try {
      const res  = await fetch('/get-contacts');
      const data = await res.json();
      if (!data.success || !data.contacts.length) return;

      const container = document.getElementById('contact-buttons');
      const wrapper   = document.getElementById('contact-options');
      container.innerHTML = '';

      data.contacts.forEach((c, idx) => {
        const btn = document.createElement('button');
        btn.className   = 'contact-btn';
        btn.type        = 'button';
        btn.innerHTML   = `<span>📱 ${c.masked}</span><span class="contact-type">${c.type}</span>`;
        btn.onclick = () => {
          // Highlight selected button and store its index
          container.querySelectorAll('.contact-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          _selectedContactIndex = idx;
          // Clear manual input to avoid confusion
          const phoneInput = document.getElementById('phone');
          phoneInput.value = '';
          phoneInput.placeholder = `Using: ${c.masked}`;
        };
        container.appendChild(btn);
      });

      wrapper.style.display = 'block';
    } catch (e) {
      // silently ignore – manual entry still works
    }
  }

  // Expose functions to global scope for inline onclick handlers
  window.verifyRegistration = verifyRegistration;
  window.verifyPhone = verifyPhone;
  window.verifyOTP = verifyOTP;
  window.goBack = goBack;

  // Allow Enter key on inputs
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const active = document.querySelector('.step-panel.active');
    if (!active) return;
    const id = active.id;
    if (id === 'panel-1') verifyRegistration();
    else if (id === 'panel-2') verifyPhone();
    else if (id === 'panel-3') verifyOTP();
  });
}

/* ══════════════════════════════════════════════════
   CHAT PAGE
   ══════════════════════════════════════════════════ */
if (IS_CHAT) {

  const messagesEl = document.getElementById('messages');
  let typingEl = null;

  // Welcome message
  window.addEventListener('DOMContentLoaded', () => {
    appendBot(
      "👋 <b>Welcome to the Academic Portal!</b><br>" +
      "I can help you with attendance, marks, CGPA, exams, fees, and more.<br>" +
      "Type <b>help</b> to see all available options, or use the quick buttons on the left."
    );
  });

  function appendMsg(type, html) {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg ' + type;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = type === 'bot' ? '🤖' : '👤';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = html;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrapper;
  }

  function appendBot(html)  { return appendMsg('bot',  html); }
  function appendUser(html) { return appendMsg('user', escapeHtml(html)); }

  function showTyping() {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg bot';
    wrapper.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    typingEl = wrapper;
  }

  function removeTyping() {
    if (typingEl) { typingEl.remove(); typingEl = null; }
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  async function sendMessage() {
    const input = document.getElementById('user-input');
    const text  = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = 'auto';
    appendUser(text);
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      removeTyping();

      if (data.logout) {
        appendBot(data.reply);
        setTimeout(() => { window.location.href = '/'; }, 1800);
        return;
      }

      if (data.success) {
        appendBot(data.reply);
      } else {
        appendBot('⚠️ ' + (data.message || 'Something went wrong.'));
      }
    } catch (e) {
      removeTyping();
      appendBot('⚠️ Network error. Please check your connection.');
    }
  }

  function sendQuick(msg) {
    document.getElementById('user-input').value = msg;
    sendMessage();
    // On mobile, close sidebar after click
    document.querySelector('.sidebar')?.classList.remove('open');
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
    // Auto-resize textarea
    const ta = document.getElementById('user-input');
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
  }

  function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
  }

  /* ── Language Selection ──────────────────────────── */
  // speechLocale is kept in sync with the selected language
  let currentSpeechLocale = 'en-US';

  async function setLanguage(langValue) {
    try {
      const res = await fetch('/set-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: langValue }),
      });
      const data = await res.json();
      if (data.success) {
        currentSpeechLocale = data.speech_locale || 'en-US';
        // Show a brief confirmation in the chat
        const labels = { english: 'English', hindi: 'Hindi (हिन्दी)', telugu: 'Telugu (తెలుగు)' };
        appendBot('🌐 Language set to <b>' + (labels[langValue] || langValue) + '</b>. Bot replies will now appear in this language.');
      }
    } catch (e) {
      appendBot('⚠️ Could not change language. Please try again.');
    }
  }

  /* ── Voice Recorder ─────────────────────────────── */
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isRecording = false;

  function toggleVoice() {
    const micBtn = document.getElementById('mic-btn');

    if (!SpeechRecognition) {
      appendBot('⚠️ Voice input is not supported by your browser. Please use Chrome or Edge.');
      return;
    }

    if (isRecording) {
      // Stop recording
      recognition.stop();
      return;
    }

    // Start recording
    recognition = new SpeechRecognition();
    recognition.lang = currentSpeechLocale;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      isRecording = true;
      micBtn.classList.add('recording');
      micBtn.title = 'Recording… click to stop';
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('user-input').value = transcript;
      // Auto-resize textarea
      const ta = document.getElementById('user-input');
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
      // Auto-send after speech recognition
      sendMessage();
    };

    recognition.onerror = (event) => {
      const msgs = {
        'not-allowed':   'Microphone access denied. Please allow microphone permission.',
        'no-speech':     'No speech detected. Please try again.',
        'network':       'Network error during voice recognition.',
      };
      appendBot('⚠️ ' + (msgs[event.error] || 'Voice error: ' + event.error));
    };

    recognition.onend = () => {
      isRecording = false;
      micBtn.classList.remove('recording');
      micBtn.title = 'Voice Input';
    };

    recognition.start();
  }

  // Expose to global scope for inline onclick handlers
  window.setLanguage  = setLanguage;
  window.toggleVoice  = toggleVoice;
  window.toggleSidebar = toggleSidebar;
}
