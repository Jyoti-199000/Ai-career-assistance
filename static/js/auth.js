/**
 * Edumart - Authentication JS
 * Handles Login and Signup AJAX
 */
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');

    // Helper: Password Visibility
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.getElementById(btn.dataset.target);
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });
    });

    // 1. Signup Flow
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('signupBtn');
            const loader = btn.querySelector('.btn-loader');
            const text = btn.querySelector('.btn-text');
            const errorAlert = document.getElementById('signupError');

            const data = {
                username: signupForm.signupUsername.value,
                email: signupForm.signupEmail.value,
                first_name: signupForm.firstName.value,
                last_name: signupForm.lastName.value,
                password: signupForm.signupPassword.value,
                password_confirm: signupForm.signupPasswordConfirm.value
            };

            // Basic validation
            if (data.password !== data.password_confirm) {
                showError(errorAlert, 'Passwords do not match');
                return;
            }

            setLoading(true, btn, loader, text);
            errorAlert.style.display = 'none';

            try {
                const res = await fetch('/auth/api/signup/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.EDUMART.csrfToken
                    },
                    body: JSON.stringify(data)
                });

                const result = await res.json();
                if (result.success) {
                    localStorage.setItem('access_token', result.tokens.access);
                    localStorage.setItem('refresh_token', result.tokens.refresh);
                    window.location.href = '/dashboard/';
                } else {
                    const errorMsg = Object.values(result.errors).flat().join(' ');
                    showError(errorAlert, errorMsg);
                }
            } catch (err) {
                showError(errorAlert, 'Network error. Please try again.');
            } finally {
                setLoading(false, btn, loader, text);
            }
        });
    }

    // 2. Login Flow
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            const loader = btn.querySelector('.btn-loader');
            const text = btn.querySelector('.btn-text');
            const errorAlert = document.getElementById('loginError');

            const data = {
                username: loginForm.loginUsername.value,
                password: loginForm.loginPassword.value,
                remember_me: loginForm.rememberMe.checked
            };

            setLoading(true, btn, loader, text);
            errorAlert.style.display = 'none';

            try {
                const res = await fetch('/auth/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.EDUMART.csrfToken
                    },
                    body: JSON.stringify(data)
                });

                const result = await res.json();
                if (result.success) {
                    localStorage.setItem('access_token', result.tokens.access);
                    localStorage.setItem('refresh_token', result.tokens.refresh);
                    window.location.href = '/dashboard/';
                } else {
                    showError(errorAlert, result.errors.detail || 'Invalid credentials');
                }
            } catch (err) {
                showError(errorAlert, 'Network error. Please try again.');
            } finally {
                setLoading(false, btn, loader, text);
            }
        });
    }

    // Utils
    function setLoading(isLoading, btn, loader, text) {
        btn.disabled = isLoading;
        loader.style.display = isLoading ? 'inline-flex' : 'none';
        text.style.display = isLoading ? 'none' : 'inline-block';
    }

    function showError(el, msg) {
        el.style.display = 'flex';
        el.querySelector('span').textContent = msg;
    }
});
