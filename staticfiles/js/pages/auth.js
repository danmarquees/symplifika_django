// Authentication Pages JavaScript Functionality

document.addEventListener("DOMContentLoaded", function () {
    // Initialize auth page functionality
    AuthPage.init();
});

const AuthPage = {
    init() {
        this.setupFormValidation();
        this.setupPasswordToggle();
        this.setupFloatingLabels();
        this.setupSubmitHandler();
        this.setupDemoCredentials();
        this.setupFormAnimations();
        this.setupAccessibility();
    },

    // Form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');

        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[required]');

            inputs.forEach(input => {
                // Real-time validation
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));

                // Add floating label functionality
                this.setupFieldLabels(input);
            });

            // Form submission
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.focusFirstError(form);
                }
            });
        });
    },

    // Validate individual field
    validateField(field) {
        const value = field.value.trim();
        const fieldContainer = field.closest('.form-field') || field.parentNode;
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        }
        // Email validation
        else if (field.type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Digite um email válido';
        }
        // Password validation
        else if (field.type === 'password' && value && value.length < 6) {
            isValid = false;
            errorMessage = 'A senha deve ter pelo menos 6 caracteres';
        }
        // Username validation
        else if (field.name === 'username' && value && value.length < 3) {
            isValid = false;
            errorMessage = 'O nome de usuário deve ter pelo menos 3 caracteres';
        }

        if (isValid) {
            this.showFieldSuccess(fieldContainer, field);
        } else {
            this.showFieldError(fieldContainer, field, errorMessage);
        }

        return isValid;
    },

    // Validate entire form
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    },

    // Show field error
    showFieldError(container, field, message) {
        container.classList.add('error');
        container.classList.remove('success');
        field.classList.add('border-red-500');

        let errorElement = container.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-message text-red-400 text-sm mt-1 block';
            container.appendChild(errorElement);
        }

        errorElement.textContent = message;

        // Add shake animation
        field.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            field.style.animation = '';
        }, 500);
    },

    // Show field success
    showFieldSuccess(container, field) {
        container.classList.remove('error');
        container.classList.add('success');
        field.classList.remove('border-red-500');
        field.classList.add('border-green-500');

        const errorElement = container.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    },

    // Clear field error
    clearFieldError(field) {
        const container = field.closest('.form-field') || field.parentNode;
        container.classList.remove('error');
        field.classList.remove('border-red-500');

        const errorElement = container.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    },

    // Focus first error field
    focusFirstError(form) {
        const firstError = form.querySelector('.error input');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    },

    // Email validation
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Password visibility toggle
    setupPasswordToggle() {
        const passwordFields = document.querySelectorAll('input[type="password"]');

        passwordFields.forEach(field => {
            const container = field.parentNode;

            // Create toggle button if it doesn't exist
            let toggleBtn = container.querySelector('.password-toggle');
            if (!toggleBtn) {
                toggleBtn = document.createElement('button');
                toggleBtn.type = 'button';
                toggleBtn.className = 'password-toggle';
                toggleBtn.innerHTML = this.getEyeIcon(false);
                toggleBtn.setAttribute('aria-label', 'Mostrar senha');
                container.style.position = 'relative';
                container.appendChild(toggleBtn);
            }

            toggleBtn.addEventListener('click', () => {
                const isPassword = field.type === 'password';
                field.type = isPassword ? 'text' : 'password';
                toggleBtn.innerHTML = this.getEyeIcon(!isPassword);
                toggleBtn.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
            });
        });
    },

    // Get eye icon SVG
    getEyeIcon(isVisible) {
        if (isVisible) {
            return `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
            `;
        } else {
            return `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
            `;
        }
    },

    // Floating labels setup
    setupFloatingLabels() {
        const fields = document.querySelectorAll('.form-field input');

        fields.forEach(field => {
            const label = field.nextElementSibling;
            if (label && label.tagName === 'LABEL') {
                const container = field.parentNode;
                container.classList.add('floating-label');

                // Check initial state
                this.updateFloatingLabel(field, label);

                // Update on input
                field.addEventListener('input', () => {
                    this.updateFloatingLabel(field, label);
                });

                field.addEventListener('focus', () => {
                    label.classList.add('focused');
                });

                field.addEventListener('blur', () => {
                    label.classList.remove('focused');
                    this.updateFloatingLabel(field, label);
                });
            }
        });
    },

    // Update floating label state
    updateFloatingLabel(field, label) {
        if (field.value.trim() || field === document.activeElement) {
            label.classList.add('floating');
        } else {
            label.classList.remove('floating');
        }
    },

    // Setup field labels
    setupFieldLabels(field) {
        const container = field.closest('.form-field') || field.parentNode;
        container.classList.add('form-field');
    },

    // Form submission handler
    setupSubmitHandler() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                const btnText = submitBtn.querySelector('#loginBtnText, #registerBtnText') || submitBtn;
                const spinner = submitBtn.querySelector('#loginSpinner, #registerSpinner, .spinner');

                if (submitBtn && !submitBtn.disabled) {
                    // Show loading state
                    submitBtn.disabled = true;
                    submitBtn.classList.add('loading');

                    if (btnText && btnText.textContent) {
                        btnText.dataset.originalText = btnText.textContent;
                        btnText.textContent = 'Processando...';
                    }

                    if (spinner) {
                        spinner.classList.remove('hidden');
                    }

                    // Reset after timeout to prevent permanent disabled state
                    setTimeout(() => {
                        this.resetSubmitButton(submitBtn, btnText, spinner);
                    }, 10000);
                }
            });
        });
    },

    // Reset submit button
    resetSubmitButton(submitBtn, btnText, spinner) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');

        if (btnText && btnText.dataset.originalText) {
            btnText.textContent = btnText.dataset.originalText;
        }

        if (spinner) {
            spinner.classList.add('hidden');
        }
    },

    // Demo credentials functionality
    setupDemoCredentials() {
        window.fillDemoCredentials = () => {
            const usernameField = document.querySelector('input[name="username"]');
            const passwordField = document.querySelector('input[name="password"]');

            if (usernameField) {
                usernameField.value = 'demo';
                usernameField.dispatchEvent(new Event('input'));
                this.updateFloatingLabel(usernameField, usernameField.nextElementSibling);
            }

            if (passwordField) {
                passwordField.value = 'demo123';
                passwordField.dispatchEvent(new Event('input'));
                this.updateFloatingLabel(passwordField, passwordField.nextElementSibling);
            }

            // Show feedback
            if (window.Symplifika && window.Symplifika.Toast) {
                window.Symplifika.Toast.info('Credenciais de demonstração preenchidas');
            }

            // Focus first field
            if (usernameField) {
                usernameField.focus();
            }
        };
    },

    // Form animations
    setupFormAnimations() {
        const formContainer = document.querySelector('.auth-form-container');
        if (formContainer) {
            // Add entrance animation
            formContainer.style.opacity = '0';
            formContainer.style.transform = 'translateY(20px)';

            setTimeout(() => {
                formContainer.style.transition = 'all 0.6s ease-out';
                formContainer.style.opacity = '1';
                formContainer.style.transform = 'translateY(0)';
            }, 100);
        }

        // Animate form fields
        const fields = document.querySelectorAll('.form-field');
        fields.forEach((field, index) => {
            field.style.opacity = '0';
            field.style.transform = 'translateX(-20px)';

            setTimeout(() => {
                field.style.transition = 'all 0.4s ease-out';
                field.style.opacity = '1';
                field.style.transform = 'translateX(0)';
            }, 200 + (index * 100));
        });
    },

    // Accessibility enhancements
    setupAccessibility() {
        // Add ARIA labels
        const passwordToggles = document.querySelectorAll('.password-toggle');
        passwordToggles.forEach(toggle => {
            toggle.setAttribute('tabindex', '0');

            // Keyboard support
            toggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggle.click();
                }
            });
        });

        // Announce form errors to screen readers
        const form = document.querySelector('form[data-validate]');
        if (form) {
            const announcer = document.createElement('div');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'sr-only';
            document.body.appendChild(announcer);

            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    const errors = form.querySelectorAll('.error-message');
                    if (errors.length > 0) {
                        announcer.textContent = `Formulário contém ${errors.length} erro(s). Verifique os campos destacados.`;
                    }
                }
            });
        }

        // Auto-focus management
        const firstInput = document.querySelector('input:not([type="hidden"])');
        if (firstInput && !firstInput.value) {
            setTimeout(() => firstInput.focus(), 500);
        }
    }
};

// Utility functions for auth pages
const AuthUtils = {
    // Generate secure password
    generatePassword(length = 12) {
        const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        let password = '';
        for (let i = 0; i < length; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return password;
    },

    // Check password strength
    checkPasswordStrength(password) {
        let strength = 0;
        const checks = [
            /.{8,}/, // At least 8 characters
            /[a-z]/, // Lowercase
            /[A-Z]/, // Uppercase
            /[0-9]/, // Numbers
            /[^a-zA-Z0-9]/ // Special characters
        ];

        checks.forEach(check => {
            if (check.test(password)) strength++;
        });

        return {
            score: strength,
            level: strength < 2 ? 'weak' : strength < 4 ? 'medium' : 'strong'
        };
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textArea);
            return success;
        }
    }
};

// Export for global access
window.AuthPage = AuthPage;
window.AuthUtils = AuthUtils;

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Re-focus form if needed
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName === 'INPUT') {
            activeElement.blur();
            setTimeout(() => activeElement.focus(), 100);
        }
    }
});
