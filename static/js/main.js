/* ============================================================
   AI Career Assistant — JavaScript Core
   Handles: Navigation, Scroll Reveals, AJAX, Chat, Code Editor
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Navbar scroll effect ---------- */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  /* ---------- Mobile toggle ---------- */
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks  = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  /* ---------- Scroll reveal ---------- */
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => observer.observe(el));
  }

  /* ---------- CSRF helper ---------- */
  function getCookie(name) {
    let value = null;
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) value = decodeURIComponent(c.substring(name.length + 1));
    });
    return value;
  }
  const csrftoken = getCookie('csrftoken');

  /* ---------- Generic POST helper ---------- */
  async function postJSON(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify(data),
    });
    return res.json();
  }

  /* ====================================================
     RESUME ANALYZER
     ==================================================== */
  const resumeForm = document.getElementById('resumeForm');
  if (resumeForm) {
    resumeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = document.getElementById('resumeText').value.trim();
      if (!text) return;

      const loading  = document.getElementById('resumeLoading');
      const results  = document.getElementById('resumeResults');
      results.style.display = 'none';
      loading.classList.add('active');

      try {
        const data = await postJSON('/api/analyze-resume/', { resume_text: text });
        renderResumeResults(data);
        results.style.display = 'block';
      } catch {
        results.innerHTML = '<p style="color:var(--accent-pink)">Something went wrong. Please try again.</p>';
        results.style.display = 'block';
      } finally {
        loading.classList.remove('active');
      }
    });
  }

  function renderResumeResults(data) {
    const c = document.getElementById('resumeResults');
    c.innerHTML = `
      <div class="result-section">
        <h3><i class="fas fa-check-circle"></i> Extracted Skills</h3>
        <div>${(data.skills || []).map(s => `<span class="tag">${s}</span>`).join(' ')}</div>
      </div>
      <div class="result-section">
        <h3><i class="fas fa-exclamation-triangle"></i> Missing Skills</h3>
        <div>${(data.missing_skills || []).map(s => `<span class="tag pink">${s}</span>`).join(' ')}</div>
      </div>
      <div class="result-section">
        <h3><i class="fas fa-lightbulb"></i> Improvement Tips</h3>
        <ul>${(data.improvements || []).map(t => `<li>${t}</li>`).join('')}</ul>
      </div>
      <div class="result-section">
        <h3><i class="fas fa-briefcase"></i> Suitable Roles</h3>
        <ul>${(data.roles || []).map(r => `<li>${r}</li>`).join('')}</ul>
      </div>
      <div class="result-section">
        <h3><i class="fas fa-search"></i> ATS Tips</h3>
        <ul>${(data.ats_tips || []).map(t => `<li>${t}</li>`).join('')}</ul>
      </div>
    `;
  }

  /* ====================================================
     ROADMAP GENERATOR
     ==================================================== */
  const roadmapForm = document.getElementById('roadmapForm');
  if (roadmapForm) {
    roadmapForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const goal   = document.getElementById('goalInput').value.trim();
      const skills = document.getElementById('skillsInput').value.trim();
      if (!goal) return;

      const loading = document.getElementById('roadmapLoading');
      const results = document.getElementById('roadmapResults');
      results.style.display = 'none';
      loading.classList.add('active');

      try {
        const data = await postJSON('/api/generate-roadmap/', { goal, skills });
        renderRoadmap(data);
        results.style.display = 'block';
      } catch {
        results.innerHTML = '<p style="color:var(--accent-pink)">Something went wrong.</p>';
        results.style.display = 'block';
      } finally {
        loading.classList.remove('active');
      }
    });
  }

  function renderRoadmap(data) {
    const c = document.getElementById('roadmapResults');
    const weeks = data.weeks || [];
    c.innerHTML = `
      <div class="roadmap-timeline">
        ${weeks.map(w => `
          <div class="roadmap-week">
            <h4>${w.title}</h4>
            <ul>${w.tasks.map(t => `<li>${t}</li>`).join('')}</ul>
            ${w.project ? `<p style="margin-top:10px;color:var(--accent-green);font-size:.85rem"><strong>🚀 Mini Project:</strong> ${w.project}</p>` : ''}
            ${w.resources ? `<p style="margin-top:6px;color:var(--accent-cyan);font-size:.82rem"><strong>📚 Resources:</strong> ${w.resources}</p>` : ''}
          </div>
        `).join('')}
      </div>
    `;
  }

  /* ====================================================
     MOCK INTERVIEW
     ==================================================== */
  const interviewForm = document.getElementById('interviewStartForm');
  if (interviewForm) {
    interviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const role = document.getElementById('roleInput').value.trim();
      if (!role) return;

      document.getElementById('interviewSetup').style.display = 'none';
      document.getElementById('interviewChat').style.display = 'block';

      const chat = document.getElementById('chatContainer');
      chat.innerHTML = '';
      addBubble('ai', `Great! Let's start the mock interview for <strong>${role}</strong>. I'll ask you 5 questions. Let's begin! 🎯`);

      try {
        const data = await postJSON('/api/interview/', { role });
        window._interviewData = data.questions || [];
        window._currentQ = 0;
        askNext();
      } catch {
        addBubble('ai', 'Sorry, something went wrong starting the interview.');
      }
    });
  }

  function askNext() {
    const qs = window._interviewData;
    const idx = window._currentQ;
    if (idx >= qs.length) {
      addBubble('ai', '🎉 Interview complete! Great job. Review the feedback above and keep practicing!');
      document.getElementById('chatInputArea').style.display = 'none';
      return;
    }
    setTimeout(() => {
      addBubble('ai', `<strong>Q${idx+1}:</strong> ${qs[idx].question}`);
    }, 600);
  }

  const chatSendBtn = document.getElementById('chatSend');
  if (chatSendBtn) {
    chatSendBtn.addEventListener('click', sendAnswer);
    document.getElementById('chatInput')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendAnswer();
    });
  }

  function sendAnswer() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';

    addBubble('user', text);

    const qs = window._interviewData;
    const idx = window._currentQ;
    if (qs && qs[idx]) {
      setTimeout(() => {
        addBubble('ai', `<strong>Feedback:</strong> ${qs[idx].feedback}<br><br><strong>Ideal Answer:</strong> ${qs[idx].ideal_answer}`);
        window._currentQ++;
        askNext();
      }, 800);
    }
  }

  function addBubble(type, html) {
    const chat = document.getElementById('chatContainer');
    const div = document.createElement('div');
    div.className = `chat-bubble ${type}`;
    div.innerHTML = html;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  /* ====================================================
     CODE EDITOR (Monaco + Piston API)
     ==================================================== */
  const editorEl = document.getElementById('monacoEditor');
  if (editorEl) {
    require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.45.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
      // Define custom dark theme
      monaco.editor.defineTheme('career-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment', foreground: '6a6a8a', fontStyle: 'italic' },
        ],
        colors: {
          'editor.background': '#0a0a1a',
          'editor.foreground': '#f0f0f8',
          'editorLineNumber.foreground': '#4a4a6a',
          'editor.selectionBackground': '#4f8cff33',
          'editor.lineHighlightBackground': '#ffffff08',
        },
      });

      window.monacoEditor = monaco.editor.create(editorEl, {
        value: '# Write your code here\nprint("Hello, World!")\n',
        language: 'python',
        theme: 'career-dark',
        fontSize: 14,
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        minimap: { enabled: false },
        padding: { top: 16 },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        smoothScrolling: true,
        cursorBlinking: 'smooth',
        cursorSmoothCaretAnimation: 'on',
        lineNumbers: 'on',
        roundedSelection: true,
      });
    });

    // Language switch
    const langSelect = document.getElementById('langSelect');
    if (langSelect) {
      const defaults = {
        python: '# Write your Python code here\nprint("Hello, World!")\n',
        javascript: '// Write your JavaScript code here\nconsole.log("Hello, World!");\n',
        java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
      };
      langSelect.addEventListener('change', () => {
        const lang = langSelect.value;
        if (window.monacoEditor) {
          monaco.editor.setModelLanguage(window.monacoEditor.getModel(), lang);
          window.monacoEditor.setValue(defaults[lang] || '');
        }
      });
    }

    // Run button
    const runBtn = document.getElementById('runCodeBtn');
    if (runBtn) {
      runBtn.addEventListener('click', async () => {
        const code = window.monacoEditor?.getValue() || '';
        const lang = document.getElementById('langSelect')?.value || 'python';
        const outputPre = document.getElementById('codeOutput');
        const statusEl  = document.getElementById('execStatus');

        outputPre.textContent = '';
        outputPre.className = '';
        statusEl.textContent = 'Running...';
        runBtn.disabled = true;

        try {
          const data = await postJSON('/api/execute-code/', { code, language: lang });
          if (data.error) {
            outputPre.textContent = data.error;
            outputPre.className = 'error';
            statusEl.textContent = 'Error';
          } else {
            outputPre.textContent = data.output || '(no output)';
            statusEl.textContent = `Done in ${data.time || '?'}`;
          }
        } catch {
          outputPre.textContent = 'Failed to connect to execution service.';
          outputPre.className = 'error';
          statusEl.textContent = 'Error';
        } finally {
          runBtn.disabled = false;
        }
      });
    }
  }

  /* ---------- Smooth scroll for anchor links ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id && id !== '#') {
        e.preventDefault();
        document.querySelector(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});
