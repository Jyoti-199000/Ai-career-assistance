/**
 * Edumart - Tools JS
 * Handles AI Resume Analysis, Roadmap Generation, and Mock Interviews
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Resume Analyzer
    const resumeForm = document.getElementById('resumeForm');
    if (resumeForm) {
        resumeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = document.getElementById('resumeText').value;
            const btn = document.getElementById('analyzeBtn');
            const results = document.getElementById('resumeResults');
            const placeholder = document.getElementById('resumePlaceholder');
            const loading = document.getElementById('resumeLoading');

            if (!text.trim()) return;

            // UI State
            loading.style.display = 'block';
            results.style.display = 'none';
            placeholder.style.display = 'none';
            btn.disabled = true;

            try {
                const res = await fetch('/api/analyze-resume/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume_text: text })
                });
                const data = await res.json();

                if (data.error) throw new Error(data.error);

                // Render Results
                results.innerHTML = `
                    <div class="results-header" style="margin-bottom:24px;">
                        <h3 style="margin-bottom:8px;"><i class="fas fa-check-circle" style="color:var(--accent-green);"></i> Analysis Complete</h3>
                        <p style="color:var(--text-secondary);">Here is what our AI found in your resume.</p>
                    </div>

                    <div class="result-section" style="margin-bottom:24px;">
                        <h4 style="font-size:.9rem;text-transform:uppercase;letter-spacing:1px;color:var(--accent-blue);margin-bottom:12px;">Detected Skills</h4>
                        <div class="skill-tags" style="display:flex;flex-wrap:wrap;gap:8px;">
                            ${data.skills.map(s => `<span class="skill-tag" style="background:rgba(79,140,255,0.1);color:var(--accent-blue);padding:4px 12px;border-radius:100px;font-size:.85rem;border:1px solid rgba(79,140,255,0.2);">${s}</span>`).join('')}
                        </div>
                    </div>

                    <div class="result-section" style="margin-bottom:24px;">
                        <h4 style="font-size:.9rem;text-transform:uppercase;letter-spacing:1px;color:var(--accent-purple);margin-bottom:12px;">Role Suggestions</h4>
                        <ul style="list-style:none;padding:0;">
                            ${data.roles.map(r => `<li style="margin-bottom:8px;display:flex;align-items:center;gap:10px;"><i class="fas fa-briefcase" style="color:var(--accent-purple);font-size:.8rem;"></i> ${r}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="result-section" style="margin-bottom:24px;">
                        <h4 style="font-size:.9rem;text-transform:uppercase;letter-spacing:1px;color:var(--accent-orange);margin-bottom:12px;">Missing Skills (Gap Analysis)</h4>
                        <div class="skill-tags" style="display:flex;flex-wrap:wrap;gap:8px;">
                            ${data.missing_skills.map(s => `<span class="skill-tag" style="background:rgba(245,158,11,0.1);color:var(--accent-orange);padding:4px 12px;border-radius:100px;font-size:.85rem;border:1px solid rgba(245,158,11,0.2);">${s}</span>`).join('')}
                        </div>
                    </div>

                    <div class="result-section">
                        <h4 style="font-size:.9rem;text-transform:uppercase;letter-spacing:1px;color:var(--accent-cyan);margin-bottom:12px;">Actionable Tips</h4>
                        <ul style="list-style:none;padding:0;">
                            ${data.improvements.map(i => `<li style="margin-bottom:12px;display:flex;gap:12px;font-size:.95rem;"><i class="fas fa-lightbulb" style="color:var(--accent-cyan);margin-top:4px;"></i> <span>${i}</span></li>`).join('')}
                        </ul>
                    </div>
                `;
                results.style.display = 'block';

            } catch (err) {
                console.error(err);
                placeholder.style.display = 'block';
                placeholder.innerHTML = `<p style="color:var(--accent-red);">Failed to analyze resume. Please try again.</p>`;
            } finally {
                loading.style.display = 'none';
                btn.disabled = false;
            }
        });
    }

    // 2. Roadmap Generator
    const roadmapForm = document.getElementById('roadmapForm');
    if (roadmapForm) {
        roadmapForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const goal = document.getElementById('goalInput').value;
            const skills = document.getElementById('skillsInput').value;
            const btn = document.getElementById('roadmapBtn');
            const results = document.getElementById('roadmapResults');
            const placeholder = document.getElementById('roadmapPlaceholder');
            const loading = document.getElementById('roadmapLoading');

            loading.style.display = 'block';
            results.style.display = 'none';
            placeholder.style.display = 'none';
            btn.disabled = true;

            try {
                const res = await fetch('/api/generate-roadmap/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ goal, skills })
                });
                const data = await res.json();

                results.innerHTML = data.weeks.map((week, idx) => `
                    <div class="roadmap-week glass" style="margin-bottom:24px;padding:24px;border-left:4px solid ${['var(--accent-blue)', 'var(--accent-purple)', 'var(--accent-pink)', 'var(--accent-cyan)'][idx % 4]}">
                        <h3 style="margin-bottom:16px;">${week.title}</h3>
                        <ul style="list-style:none;padding:0;margin-bottom:20px;">
                            ${week.tasks.map(t => `<li style="margin-bottom:10px;display:flex;gap:12px;"><i class="fas fa-check-circle" style="color:var(--accent-green);margin-top:3px;"></i> ${t}</li>`).join('')}
                        </ul>
                        <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:12px;border:1px solid var(--glass-border);">
                            <div style="font-size:.8rem;color:var(--text-secondary);text-transform:uppercase;margin-bottom:4px;">Weekly Project</div>
                            <div style="font-weight:600;margin-bottom:8px;">${week.project}</div>
                            <div style="font-size:.85rem;"><i class="fas fa-link"></i> Resources: <span style="color:var(--accent-blue);">${week.resources}</span></div>
                        </div>
                    </div>
                `).join('');
                results.style.display = 'block';
            } catch (err) {
                console.error(err);
                placeholder.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                btn.disabled = false;
            }
        });
    }

    // 3. Mock Interview
    const interviewStartForm = document.getElementById('interviewStartForm');
    if (interviewStartForm) {
        let currentQuestions = [];
        let currentIdx = 0;

        interviewStartForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const role = document.getElementById('roleInput').value;
            const setup = document.getElementById('interviewSetup');
            const chat = document.getElementById('interviewChat');
            const container = document.getElementById('chatContainer');

            setup.style.display = 'none';
            chat.style.display = 'block';

            addMessage('assistant', `Hello! I'm your AI interviewer today for the **${role}** position. Let's get started with some technical questions.`);

            try {
                const res = await fetch('/api/interview/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ role })
                });
                const data = await res.json();
                currentQuestions = data.questions;
                
                if (currentQuestions.length > 0) {
                    setTimeout(() => askNext(), 1000);
                }
            } catch (err) {
                console.error(err);
                addMessage('assistant', "I'm sorry, I encountered an error connecting to my database. Please refresh and try again.");
            }
        });

        const askNext = () => {
            if (currentIdx < currentQuestions.length) {
                addMessage('assistant', currentQuestions[currentIdx].question);
            } else {
                addMessage('assistant', "That was my last question. Great job! How do you feel about the session?");
            }
        };

        const addMessage = (role, text) => {
            const container = document.getElementById('chatContainer');
            const msg = document.createElement('div');
            msg.className = `chat-bubble ${role}`;
            msg.innerHTML = `<div class="bubble-content">${text}</div>`;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        };

        const sendBtn = document.getElementById('chatSend');
        const input = document.getElementById('chatInput');

        const handleSend = () => {
            const val = input.value.trim();
            if (!val) return;
            addMessage('user', val);
            input.value = '';

            // Provide immediate feedback if it was a question
            if (currentIdx < currentQuestions.length) {
                const q = currentQuestions[currentIdx];
                setTimeout(() => {
                    addMessage('assistant', `<div style="font-size:.85rem;opacity:.8;margin-bottom:8px;"><i class="fas fa-lightbulb"></i> Feedback: ${q.feedback}</div><div>${currentIdx < currentQuestions.length - 1 ? "Got it. Next question:" : "Understood."}</div>`);
                    currentIdx++;
                    setTimeout(() => askNext(), 1500);
                }, 800);
            }
        };

        sendBtn.addEventListener('click', handleSend);
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
    }
});
