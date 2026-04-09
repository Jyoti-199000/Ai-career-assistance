"""
Core views for CareerAI — page renders + API endpoints.
AI features use intelligent mock data so the app works out of the box.
Replace the mock logic with a real AI API (OpenAI / Gemini) when ready.
"""

import json
import os
import re
import subprocess
import tempfile
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# ─── Page Views ───────────────────────────────────────────────

def home(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def resume_page(request):
    return render(request, 'resume.html')

def roadmap_page(request):
    return render(request, 'roadmap.html')

def interview_page(request):
    return render(request, 'interview.html')

def courses_page(request):
    return render(request, 'courses.html')

def editor_page(request):
    return render(request, 'editor.html')


# ─── API: Resume Analyzer ────────────────────────────────────

@csrf_exempt
@require_POST
def api_analyze_resume(request):
    """Analyze resume text and return structured feedback."""
    try:
        body = json.loads(request.body)
        resume_text = body.get('resume_text', '').lower()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Skill extraction (keyword matching)
    all_skills = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'html', 'css', 'react', 'angular', 'vue', 'next.js', 'node.js', 'express',
        'django', 'flask', 'fastapi', 'spring boot',
        'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'firebase',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'git', 'github', 'ci/cd', 'jenkins', 'linux',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp',
        'data analysis', 'pandas', 'numpy', 'matplotlib',
        'rest api', 'graphql', 'microservices', 'agile', 'scrum',
        'figma', 'photoshop', 'ui/ux',
    ]

    found_skills = [s for s in all_skills if s in resume_text]

    # Determine domain
    web_keywords = ['html', 'css', 'react', 'angular', 'vue', 'next.js', 'node.js', 'django', 'flask']
    data_keywords = ['machine learning', 'deep learning', 'data analysis', 'pandas', 'numpy', 'tensorflow']
    devops_keywords = ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'terraform']

    is_web = any(s in found_skills for s in web_keywords)
    is_data = any(s in found_skills for s in data_keywords)
    is_devops = any(s in found_skills for s in devops_keywords)

    # Missing skills suggestion
    missing = []
    if is_web:
        for s in ['typescript', 'next.js', 'docker', 'ci/cd', 'rest api', 'git']:
            if s not in found_skills:
                missing.append(s)
    elif is_data:
        for s in ['sql', 'python', 'tensorflow', 'pytorch', 'docker', 'git']:
            if s not in found_skills:
                missing.append(s)
    elif is_devops:
        for s in ['terraform', 'kubernetes', 'linux', 'python', 'git']:
            if s not in found_skills:
                missing.append(s)
    else:
        missing = ['git', 'docker', 'rest api', 'sql', 'linux']

    # Role suggestions
    roles = []
    if is_web:
        roles = ['Frontend Developer', 'Full Stack Developer', 'Web Application Engineer', 'UI Engineer']
    elif is_data:
        roles = ['Data Scientist', 'ML Engineer', 'Data Analyst', 'AI Research Intern']
    elif is_devops:
        roles = ['DevOps Engineer', 'Cloud Engineer', 'Site Reliability Engineer', 'Platform Engineer']
    else:
        roles = ['Junior Software Developer', 'Technical Support Engineer', 'QA Analyst', 'IT Associate']

    # Improvements
    improvements = [
        'Add measurable achievements (numbers, percentages) to each experience bullet',
        'Include a professional summary section at the top highlighting 2-3 key strengths',
        'List technical projects with GitHub links to demonstrate hands-on skills',
        'Organize skills by category (Languages, Frameworks, Tools, Databases)',
        'Add relevant certifications or online course completions',
    ]

    ats_tips = [
        'Use standard section headings: "Experience", "Education", "Skills", "Projects"',
        'Avoid graphics, tables, or fancy formatting — ATSs parse plain text best',
        'Mirror keywords from the target job description in your resume',
        'Use a clean, single-column layout with consistent date formatting',
        'Save as .docx for ATS compatibility; use PDF only when specified',
    ]

    return JsonResponse({
        'skills': found_skills if found_skills else ['No specific skills detected — try pasting your full resume'],
        'missing_skills': missing[:6],
        'improvements': improvements,
        'roles': roles,
        'ats_tips': ats_tips,
    })


# ─── API: Roadmap Generator ──────────────────────────────────

@csrf_exempt
@require_POST
def api_generate_roadmap(request):
    """Generate a 4-week learning roadmap based on goal & skills."""
    try:
        body = json.loads(request.body)
        goal = body.get('goal', 'Software Developer')
        skills = body.get('skills', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    goal_lower = goal.lower()

    # Generate context-aware roadmap
    if 'frontend' in goal_lower or 'web' in goal_lower or 'full stack' in goal_lower or 'fullstack' in goal_lower:
        weeks = [
            {
                'title': '📅 Week 1 — HTML, CSS & Responsive Design',
                'tasks': [
                    'Master semantic HTML5 tags and accessibility best practices',
                    'Deep dive into CSS Flexbox and Grid layouts',
                    'Learn responsive design with media queries',
                    'Study CSS custom properties (variables) and modern selectors',
                ],
                'project': 'Build a responsive portfolio website from scratch',
                'resources': 'freeCodeCamp Responsive Web Design, MDN Web Docs',
            },
            {
                'title': '📅 Week 2 — JavaScript & DOM Manipulation',
                'tasks': [
                    'Learn JavaScript fundamentals: variables, functions, loops, arrays, objects',
                    'Understand ES6+ features: arrow functions, destructuring, template literals',
                    'Master DOM manipulation and event handling',
                    'Learn asynchronous JS: Promises, async/await, Fetch API',
                ],
                'project': 'Build an interactive to-do app with local storage',
                'resources': 'JavaScript.info, Eloquent JavaScript (free book)',
            },
            {
                'title': '📅 Week 3 — React & Component-Based Architecture',
                'tasks': [
                    'Set up a React project with Vite or Create React App',
                    'Learn components, props, state, and lifecycle concepts',
                    'Master hooks: useState, useEffect, useContext, useRef',
                    'Implement routing with React Router',
                ],
                'project': 'Build a movie search app using a public API',
                'resources': 'React Official Docs, Scrimba React Course (free)',
            },
            {
                'title': '📅 Week 4 — Backend & Deployment',
                'tasks': [
                    'Learn Node.js basics and Express.js for RESTful APIs',
                    'Connect to a database (MongoDB or PostgreSQL)',
                    'Implement authentication with JWT',
                    'Deploy your full-stack app to Vercel/Railway',
                ],
                'project': 'Build and deploy a full-stack blog application',
                'resources': 'The Odin Project, freeCodeCamp Backend Course',
            },
        ]
    elif 'data' in goal_lower or 'ml' in goal_lower or 'machine learning' in goal_lower or 'ai' in goal_lower:
        weeks = [
            {
                'title': '📅 Week 1 — Python & Data Fundamentals',
                'tasks': [
                    'Master Python data types, control flow, and functions',
                    'Learn NumPy for numerical computing',
                    'Master Pandas for data manipulation and cleaning',
                    'Practice reading CSV, JSON, and API data',
                ],
                'project': 'Analyze a real-world dataset (e.g., COVID, weather, or stock data)',
                'resources': 'freeCodeCamp Scientific Computing with Python, Kaggle Learn',
            },
            {
                'title': '📅 Week 2 — Data Visualization & Statistics',
                'tasks': [
                    'Learn Matplotlib and Seaborn for data visualization',
                    'Understand measures of central tendency and spread',
                    'Study probability distributions and hypothesis testing',
                    'Practice creating insightful dashboards',
                ],
                'project': 'Create a data visualization dashboard with 5+ chart types',
                'resources': 'Khan Academy Statistics, Kaggle Courses',
            },
            {
                'title': '📅 Week 3 — Machine Learning Basics',
                'tasks': [
                    'Understand supervised vs unsupervised learning',
                    'Learn scikit-learn: classification, regression, clustering',
                    'Practice feature engineering and model evaluation',
                    'Study cross-validation and hyperparameter tuning',
                ],
                'project': 'Build a house price prediction model',
                'resources': 'Coursera ML by Andrew Ng, fast.ai (free)',
            },
            {
                'title': '📅 Week 4 — Deep Learning & Deployment',
                'tasks': [
                    'Learn neural network fundamentals with TensorFlow/Keras',
                    'Build image classification and NLP models',
                    'Learn model serialization and REST API deployment',
                    'Deploy a ML model as a web application',
                ],
                'project': 'Build and deploy a sentiment analysis web app',
                'resources': 'TensorFlow Official Tutorials, Papers With Code',
            },
        ]
    elif 'devops' in goal_lower or 'cloud' in goal_lower or 'sre' in goal_lower:
        weeks = [
            {
                'title': '📅 Week 1 — Linux & Networking Fundamentals',
                'tasks': [
                    'Master Linux command line and shell scripting (bash)',
                    'Understand networking: TCP/IP, DNS, HTTP/HTTPS, SSH',
                    'Learn user management, permissions, and process control',
                    'Practice with a Linux VM or WSL',
                ],
                'project': 'Automate server setup with a bash script',
                'resources': 'Linux Journey, The Missing Semester (MIT)',
            },
            {
                'title': '📅 Week 2 — Docker & Containerization',
                'tasks': [
                    'Learn Docker fundamentals: images, containers, volumes, networks',
                    'Write Dockerfiles for multi-stage builds',
                    'Master Docker Compose for multi-container applications',
                    'Understand container registries and image optimization',
                ],
                'project': 'Containerize a full-stack application with Docker Compose',
                'resources': 'Docker Official Getting Started, Play with Docker',
            },
            {
                'title': '📅 Week 3 — CI/CD & Automation',
                'tasks': [
                    'Learn Git workflows (feature branches, PRs, rebasing)',
                    'Set up CI/CD pipelines with GitHub Actions',
                    'Implement automated testing in pipelines',
                    'Learn infrastructure as code basics with Terraform',
                ],
                'project': 'Create a CI/CD pipeline that tests, builds, and deploys automatically',
                'resources': 'GitHub Actions Docs, Terraform Getting Started',
            },
            {
                'title': '📅 Week 4 — Cloud & Kubernetes',
                'tasks': [
                    'Learn AWS/GCP core services (EC2, S3, IAM, VPC)',
                    'Understand Kubernetes architecture and basic objects',
                    'Deploy applications to a Kubernetes cluster',
                    'Learn monitoring with Prometheus and Grafana',
                ],
                'project': 'Deploy a microservices app to Kubernetes on a cloud provider',
                'resources': 'AWS Free Tier Labs, Kubernetes Official Tutorials',
            },
        ]
    else:
        weeks = [
            {
                'title': '📅 Week 1 — Programming Foundations',
                'tasks': [
                    'Choose a primary language (Python recommended for beginners)',
                    'Learn variables, data types, control flow, and functions',
                    'Practice with 20+ coding exercises on LeetCode Easy',
                    'Set up Git and learn version control basics',
                ],
                'project': 'Build a command-line calculator with history feature',
                'resources': 'Automate the Boring Stuff with Python (free), Codecademy',
            },
            {
                'title': '📅 Week 2 — Data Structures & Problem Solving',
                'tasks': [
                    'Learn arrays, linked lists, stacks, and queues',
                    'Understand hash tables and their applications',
                    'Practice searching and sorting algorithms',
                    'Solve 15+ problems on HackerRank or LeetCode',
                ],
                'project': 'Implement a contact management system using data structures',
                'resources': 'freeCodeCamp DSA Course, NeetCode.io',
            },
            {
                'title': '📅 Week 3 — Web Development Basics',
                'tasks': [
                    'Learn HTML5 and semantic markup',
                    'Master CSS styling, layouts (Flexbox, Grid)',
                    'JavaScript DOM manipulation and events',
                    'Build interactive web pages',
                ],
                'project': 'Build a personal portfolio website',
                'resources': 'The Odin Project, MDN Web Docs',
            },
            {
                'title': '📅 Week 4 — Projects & Interview Prep',
                'tasks': [
                    'Build 2 portfolio-worthy projects',
                    'Create a professional resume and LinkedIn profile',
                    'Practice behavioral interview questions (STAR method)',
                    'Study common technical interview patterns',
                ],
                'project': 'Full-stack CRUD application with database',
                'resources': 'Pramp (free mock interviews), interview.io',
            },
        ]

    return JsonResponse({'weeks': weeks})


# ─── API: Mock Interview ─────────────────────────────────────

@csrf_exempt
@require_POST
def api_interview(request):
    """Return interview questions with feedback for a given role."""
    try:
        body = json.loads(request.body)
        role = body.get('role', 'Software Developer').lower()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Role-specific question banks
    if 'frontend' in role or 'react' in role or 'web' in role:
        questions = [
            {
                'question': 'What is the Virtual DOM in React, and how does it improve performance?',
                'feedback': 'Focus on explaining the diffing algorithm and how it minimizes direct DOM manipulations.',
                'ideal_answer': 'The Virtual DOM is a lightweight JavaScript representation of the actual DOM. When state changes, React creates a new Virtual DOM tree, compares (diffs) it with the previous one, and only updates the changed elements in the real DOM. This batched, minimal update process is much faster than directly manipulating the DOM for every change.',
            },
            {
                'question': 'Explain the difference between CSS Flexbox and Grid. When would you use each?',
                'feedback': 'Show you understand that Flexbox is 1D and Grid is 2D, and give concrete layout examples.',
                'ideal_answer': 'Flexbox is designed for one-dimensional layouts — either a row or a column. Grid is for two-dimensional layouts — rows AND columns simultaneously. Use Flexbox for navigation bars, aligning items in a row, or simple card layouts. Use Grid for page-level layouts, dashboards, or whenever you need precise control over both axes.',
            },
            {
                'question': 'What are React hooks? Explain useState and useEffect with examples.',
                'feedback': 'Demonstrate practical understanding by describing when each hook fires and how to avoid infinite loops.',
                'ideal_answer': 'Hooks let you use state and lifecycle features in functional components. useState returns a state variable and setter function — e.g., const [count, setCount] = useState(0). useEffect runs side effects like API calls — it takes a callback and a dependency array. An empty array [] means it runs once on mount; including variables means it re-runs when they change.',
            },
            {
                'question': 'How would you optimize the performance of a React application?',
                'feedback': 'Mention specific techniques rather than general advice. Show awareness of profiling tools.',
                'ideal_answer': 'Key optimizations: (1) Use React.memo to prevent unnecessary re-renders of components. (2) useMemo and useCallback to memoize expensive computations and callbacks. (3) Code splitting with React.lazy and Suspense. (4) Virtualize long lists with react-window. (5) Optimize images with lazy loading. (6) Use React DevTools Profiler to identify bottlenecks.',
            },
            {
                'question': 'Explain the concept of closures in JavaScript with a practical example.',
                'feedback': 'A strong answer connects closures to data privacy and practical patterns like debounce or event handlers.',
                'ideal_answer': 'A closure is a function that remembers variables from its outer scope even after the outer function has returned. Example: function createCounter() { let count = 0; return () => ++count; }. Each call to createCounter() creates a new closure with its own count. Closures enable data privacy, factory functions, and patterns like debounce/throttle.',
            },
        ]
    elif 'data' in role or 'ml' in role or 'machine learning' in role:
        questions = [
            {
                'question': 'Explain the bias-variance tradeoff in machine learning.',
                'feedback': 'Use concrete examples and mention techniques to balance both.',
                'ideal_answer': 'Bias is the error from overly simple models (underfitting) — the model misses patterns. Variance is the error from overly complex models (overfitting) — the model captures noise. The tradeoff: reducing bias often increases variance and vice versa. Techniques like cross-validation, regularization (L1/L2), and ensemble methods (Random Forest, Boosting) help find the right balance.',
            },
            {
                'question': 'What is the difference between supervised and unsupervised learning? Give examples.',
                'feedback': 'Clearly define each paradigm and give at least 2 real-world examples for each.',
                'ideal_answer': 'Supervised learning uses labeled data to learn input-output mappings. Examples: spam detection (classification), house price prediction (regression). Unsupervised learning finds patterns in unlabeled data. Examples: customer segmentation (clustering), dimensionality reduction (PCA). Semi-supervised and self-supervised learning are hybrid approaches.',
            },
            {
                'question': 'How would you handle missing values in a dataset?',
                'feedback': 'Show you consider the nature and proportion of missing data before choosing a strategy.',
                'ideal_answer': 'Options: (1) Remove rows/columns if < 5% missing and MCAR. (2) Impute with mean/median for numerical, mode for categorical. (3) Use advanced imputation (KNN, MICE) for complex patterns. (4) Use models that handle missing values natively (XGBoost). Always analyze the missing pattern first: MCAR, MAR, or MNAR — this determines the best strategy.',
            },
            {
                'question': 'Explain precision, recall, and F1-score. When would you prioritize one over another?',
                'feedback': 'Connect each metric to a business scenario to show practical understanding.',
                'ideal_answer': 'Precision = TP/(TP+FP) — "of predicted positives, how many are correct?" Recall = TP/(TP+FN) — "of actual positives, how many did we find?" F1 = harmonic mean of both. Prioritize recall in medical diagnosis (missing a disease is costly). Prioritize precision in spam filters (marking real email as spam is bad). Use F1 when you need a balanced view.',
            },
            {
                'question': 'What is gradient descent, and what are its variants?',
                'feedback': 'Explain the intuition, not just the math. Mention practical considerations like learning rate.',
                'ideal_answer': 'Gradient descent is an optimization algorithm that iteratively moves toward the minimum of a loss function by following the negative gradient. Variants: (1) Batch GD — uses entire dataset per step (stable but slow). (2) Stochastic GD — one sample per step (noisy but fast). (3) Mini-batch GD — a compromise using small batches. Advanced: Adam, RMSProp, AdaGrad adaptively adjust learning rates.',
            },
        ]
    else:
        questions = [
            {
                'question': f'Tell me about a challenging project you worked on as a {role.title()}.',
                'feedback': 'Use the STAR method: Situation, Task, Action, Result. Quantify impact where possible.',
                'ideal_answer': 'A strong answer describes a specific situation with clear technical challenges, your specific actions to solve them, the tools/technologies used, and measurable outcomes (e.g., "reduced load time by 40%", "handled 10K concurrent users"). Show problem-solving skills and technical depth.',
            },
            {
                'question': 'Explain the concept of Object-Oriented Programming and its four pillars.',
                'feedback': 'Give brief definitions with code-level examples for at least two pillars.',
                'ideal_answer': 'OOP models software around objects. Four pillars: (1) Encapsulation — bundling data and methods, using access modifiers for data hiding. (2) Inheritance — child classes inherit from parent classes for code reuse. (3) Polymorphism — same interface, different implementations (method overriding/overloading). (4) Abstraction — hiding complex implementation behind clean interfaces (abstract classes, interfaces).',
            },
            {
                'question': 'What is a RESTful API? How would you design one for a to-do application?',
                'feedback': 'Show understanding of HTTP methods, resource naming, and status codes.',
                'ideal_answer': 'REST (Representational State Transfer) uses HTTP methods on resources. For a to-do app: GET /api/todos (list all), GET /api/todos/:id (get one), POST /api/todos (create), PUT /api/todos/:id (update), DELETE /api/todos/:id (delete). Use proper status codes: 200 OK, 201 Created, 404 Not Found, 422 Unprocessable Entity. Keep endpoints noun-based and stateless.',
            },
            {
                'question': 'What is the difference between SQL and NoSQL databases? When would you use each?',
                'feedback': 'Compare on structure, scalability, consistency, and use cases — avoid just listing names.',
                'ideal_answer': 'SQL databases (PostgreSQL, MySQL) are relational with fixed schemas, ACID compliance, and join operations — great for complex queries and transactional data (banking, ERP). NoSQL databases (MongoDB, Redis) offer flexible schemas, horizontal scaling, and high throughput — ideal for real-time apps, content management, and rapidly changing data models. Choice depends on data structure, consistency needs, and scale requirements.',
            },
            {
                'question': 'How do you approach debugging a complex issue in production?',
                'feedback': 'Show a systematic approach rather than random "try things" — mention logging, monitoring, and reproducing.',
                'ideal_answer': 'Systematic approach: (1) Gather information — check logs, error messages, monitoring dashboards. (2) Reproduce the issue in a staging environment. (3) Narrow scope — isolate the failing component (binary search in the call stack). (4) Form and test hypotheses. (5) Fix with minimal, targeted changes. (6) Add tests to prevent regression. (7) Document the root cause and fix in a post-mortem.',
            },
        ]

    return JsonResponse({'questions': questions})


# ─── API: Code Execution (Local Subprocess) ──────────────────

@csrf_exempt
@require_POST
def api_execute_code(request):
    """Execute code locally using subprocess with timeout safety."""
    try:
        body = json.loads(request.body)
        code = body.get('code', '')
        language = body.get('language', 'python')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not code.strip():
        return JsonResponse({'error': 'No code provided.'}, status=400)

    TIMEOUT = 10  # seconds

    try:
        if language == 'python':
            result = _run_python(code, TIMEOUT)
        elif language == 'javascript':
            result = _run_javascript(code, TIMEOUT)
        elif language == 'java':
            result = _run_java(code, TIMEOUT)
        else:
            return JsonResponse({'error': f'Unsupported language: {language}'}, status=400)

        return JsonResponse(result)

    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'Execution timed out (10 second limit).', 'time': '—'})
    except FileNotFoundError as e:
        return JsonResponse({
            'error': f'Runtime not found. Make sure {language} is installed on your system.\n{str(e)}',
            'time': '—',
        })
    except Exception as e:
        return JsonResponse({'error': f'Execution error: {str(e)}', 'time': '—'})


def _run_python(code, timeout):
    """Execute Python code via subprocess."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        tmp_path = f.name
    try:
        start = time.time()
        proc = subprocess.run(
            ['python', tmp_path],
            capture_output=True, text=True, timeout=timeout,
            cwd=tempfile.gettempdir(),
        )
        elapsed = round(time.time() - start, 2)
        if proc.returncode != 0:
            return {'error': proc.stderr or 'Runtime error', 'time': f'{elapsed}s'}
        output = proc.stdout
        if proc.stderr:
            output += '\n--- stderr ---\n' + proc.stderr
        return {'output': output or '(no output)', 'time': f'{elapsed}s'}
    finally:
        os.unlink(tmp_path)


def _run_javascript(code, timeout):
    """Execute JavaScript code via Node.js."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(code)
        tmp_path = f.name
    try:
        start = time.time()
        proc = subprocess.run(
            ['node', tmp_path],
            capture_output=True, text=True, timeout=timeout,
            cwd=tempfile.gettempdir(),
        )
        elapsed = round(time.time() - start, 2)
        if proc.returncode != 0:
            return {'error': proc.stderr or 'Runtime error', 'time': f'{elapsed}s'}
        output = proc.stdout
        if proc.stderr:
            output += '\n--- stderr ---\n' + proc.stderr
        return {'output': output or '(no output)', 'time': f'{elapsed}s'}
    finally:
        os.unlink(tmp_path)


def _run_java(code, timeout):
    """Compile and execute Java code."""
    tmp_dir = tempfile.mkdtemp()
    java_file = os.path.join(tmp_dir, 'Main.java')
    try:
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(code)

        # Compile
        start = time.time()
        compile_proc = subprocess.run(
            ['javac', java_file],
            capture_output=True, text=True, timeout=timeout,
            cwd=tmp_dir,
        )
        if compile_proc.returncode != 0:
            elapsed = round(time.time() - start, 2)
            return {'error': compile_proc.stderr or 'Compilation error', 'time': f'{elapsed}s'}

        # Run
        run_proc = subprocess.run(
            ['java', '-cp', tmp_dir, 'Main'],
            capture_output=True, text=True, timeout=timeout,
            cwd=tmp_dir,
        )
        elapsed = round(time.time() - start, 2)
        if run_proc.returncode != 0:
            return {'error': run_proc.stderr or 'Runtime error', 'time': f'{elapsed}s'}
        output = run_proc.stdout
        if run_proc.stderr:
            output += '\n--- stderr ---\n' + run_proc.stderr
        return {'output': output or '(no output)', 'time': f'{elapsed}s'}
    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

