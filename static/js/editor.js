/**
 * Edumart - Code Editor JS
 * Initializes Monaco Editor and handles code execution
 */
document.addEventListener('DOMContentLoaded', () => {
    const editorContainer = document.getElementById('monacoEditor');
    if (!editorContainer) return;

    let editor;
    const langSelect = document.getElementById('langSelect');
    const runBtn = document.getElementById('runCodeBtn');
    const output = document.getElementById('codeOutput');
    const status = document.getElementById('execStatus');

    // Default snippets
    const snippets = {
        python: 'print("Hello from Edumart AI!")\n\ndef greet(name):\n    return f"Welcome to the career assistant, {name}!"\n\nprint(greet("Developer"))',
        javascript: 'console.log("Hello from Edumart AI!");\n\nfunction greet(name) {\n    return `Welcome to the career assistant, ${name}!`;\n}\n\nconsole.log(greet("Developer"));',
        java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Edumart AI!");\n    }\n}'
    };

    // Load Monaco
    require.config({ paths: { 'vs': 'https://unpkg.com/monaco-editor@0.45.0/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        editor = monaco.editor.create(editorContainer, {
            value: snippets.python,
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
            fontSize: 14,
            fontFamily: '"JetBrains Mono", monospace',
            minimap: { enabled: false },
            padding: { top: 20 }
        });

        // Theme sync
        const currentTheme = document.documentElement.getAttribute('data-theme');
        monaco.editor.setTheme(currentTheme === 'light' ? 'vs' : 'vs-dark');
    });

    // Language Change
    langSelect.addEventListener('change', () => {
        const lang = langSelect.value;
        const model = editor.getModel();
        monaco.editor.setModelLanguage(model, lang);
        editor.setValue(snippets[lang] || '');
    });

    // Run Code
    runBtn.addEventListener('click', async () => {
        const code = editor.getValue();
        const lang = langSelect.value;

        runBtn.disabled = true;
        runBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        status.textContent = 'Executing...';
        status.style.color = 'var(--accent-orange)';
        output.textContent = 'Running your code...';

        try {
            const res = await fetch('/api/execute-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.EDUMART.csrfToken
                },
                body: JSON.stringify({ code, language: lang })
            });

            const result = await res.json();
            output.textContent = result.output || result.error || 'No output received.';
            status.textContent = result.error ? 'Error' : 'Success';
            status.style.color = result.error ? '#f87171' : 'var(--accent-green)';
        } catch (err) {
            output.textContent = 'Error connecting to the execution server.';
            status.textContent = 'Failed';
            status.style.color = '#f87171';
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fas fa-play"></i> Run Code';
        }
    });

    // Observe theme changes
    const observer = new MutationObserver(() => {
        const theme = document.documentElement.getAttribute('data-theme');
        if (editor) {
            monaco.editor.setTheme(theme === 'light' ? 'vs' : 'vs-dark');
        }
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
});
