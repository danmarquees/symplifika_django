// Symplifika Landing Page - Main JavaScript

// Configuration
const LANDING_CONFIG = {
    API_ENDPOINTS: {
        WAITLIST: '/api/waitlist',
        ANALYTICS: '/api/analytics'
    },
    ANIMATION_DURATION: 300,
    SCROLL_OFFSET: 100,
    COUNTER_UPDATE_INTERVAL: 5000
};

// State management
const AppState = {
    isLoading: false,
    waitlistCount: 127,
    userLocation: null,
    hasSubmitted: false
};

// Utility functions
const Utils = {
    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Format numbers
    formatNumber(num) {
        return new Intl.NumberFormat('pt-BR').format(num);
    },

    // Validate email
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Get user location (for analytics)
    async getUserLocation() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            return {
                country: data.country_name,
                city: data.city,
                timezone: data.timezone
            };
        } catch (error) {
            console.warn('Could not get user location:', error);
            return null;
        }
    },

    // Track events (placeholder for analytics)
    trackEvent(eventName, properties = {}) {
        // In production, integrate with Google Analytics, Mixpanel, etc.
        console.log('Event tracked:', eventName, properties);

        // Example: Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'Landing Page',
                ...properties
            });
        }
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 max-w-sm p-4 mb-4 text-white rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;

        const bgColors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        toast.classList.add(bgColors[type] || bgColors.info);
        toast.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    ${this.getToastIcon(type)}
                </div>
                <div class="ml-3 text-sm font-medium">${message}</div>
                <button class="ml-auto -mx-1.5 -my-1.5 text-white hover:bg-white/20 rounded-lg p-1.5">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Auto hide after 5 seconds
        const autoHide = setTimeout(() => {
            this.hideToast(toast);
        }, 5000);

        // Close button functionality
        const closeButton = toast.querySelector('button');
        closeButton.addEventListener('click', () => {
            clearTimeout(autoHide);
            this.hideToast(toast);
        });
    },

    getToastIcon(type) {
        const icons = {
            success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
            error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
            warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
            info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
        };
        return icons[type] || icons.info;
    },

    hideToast(toast) {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
};

// Animation controller
const AnimationController = {
    // Initialize intersection observer for scroll animations
    init() {
        this.setupScrollAnimations();
        this.setupParallaxEffects();
        this.setupCounterAnimations();
    },

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    element.classList.add('animate-fade-in');

                    // Add stagger delay for multiple elements
                    if (element.dataset.delay) {
                        element.style.animationDelay = element.dataset.delay + 'ms';
                    }
                }
            });
        }, observerOptions);

        // Observe animated elements
        const animatedElements = document.querySelectorAll(
            '.group, .faq-item, .card-hover, [data-animate="true"]'
        );

        animatedElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            el.dataset.delay = index * 100; // Stagger animation
            observer.observe(el);
        });
    },

    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');

        if (parallaxElements.length === 0) return;

        const handleScroll = Utils.throttle(() => {
            const scrolled = window.pageYOffset;

            parallaxElements.forEach(el => {
                const rate = scrolled * -0.5;
                el.style.transform = `translateY(${rate}px)`;
            });
        }, 16); // ~60fps

        window.addEventListener('scroll', handleScroll);
    },

    setupCounterAnimations() {
        const counters = document.querySelectorAll('[data-counter]');

        counters.forEach(counter => {
            const target = parseInt(counter.dataset.counter);
            const duration = parseInt(counter.dataset.duration) || 2000;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(counter, 0, target, duration);
                        observer.unobserve(counter);
                    }
                });
            });

            observer.observe(counter);
        });
    },

    animateCounter(element, start, end, duration) {
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const current = Math.floor(start + (end - start) * this.easeOutCubic(progress));
            element.textContent = Utils.formatNumber(current);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    },

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
};

// Waitlist form handler
const WaitlistForm = {
    init() {
        this.form = document.getElementById('waitlist-form');
        this.submitButton = document.getElementById('submit-btn');
        this.successMessage = document.getElementById('success-message');

        if (this.form) {
            this.setupEventListeners();
        }
    },

    setupEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));

        // Real-time validation
        const inputs = this.form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    },

    async handleSubmit(e) {
        e.preventDefault();

        if (AppState.hasSubmitted) {
            Utils.showToast('Você já está na nossa lista de espera!', 'info');
            return;
        }

        if (!this.validateForm()) {
            return;
        }

        this.setLoading(true);

        const formData = new FormData(this.form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            role: formData.get('role'),
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            referrer: document.referrer || 'direct',
            location: AppState.userLocation
        };

        try {
            // Track form submission
            Utils.trackEvent('waitlist_form_submitted', {
                role: data.role,
                referrer: data.referrer
            });

            // Simulate API call (replace with real endpoint)
            await this.submitToWaitlist(data);

            this.showSuccess();
            this.updateWaitlistCount();
            AppState.hasSubmitted = true;

            // Store in localStorage to prevent double submissions
            localStorage.setItem('symplifika_waitlist_submitted', 'true');

        } catch (error) {
            console.error('Waitlist submission error:', error);
            Utils.showToast('Ops! Algo deu errado. Tente novamente.', 'error');
        } finally {
            this.setLoading(false);
        }
    },

    async submitToWaitlist(data) {
        // Replace this with your actual API endpoint
        // For now, we'll simulate a successful submission
        return new Promise((resolve) => {
            setTimeout(() => {
                console.log('Waitlist data submitted:', data);
                resolve({ success: true });
            }, 1500);
        });

        // Real implementation would be:
        /*
        const response = await fetch(LANDING_CONFIG.API_ENDPOINTS.WAITLIST, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response.json();
        */
    },

    validateForm() {
        const name = this.form.querySelector('#name').value.trim();
        const email = this.form.querySelector('#email').value.trim();
        const role = this.form.querySelector('#role').value;

        let isValid = true;

        if (!name || name.length < 2) {
            this.showFieldError('name', 'Nome deve ter pelo menos 2 caracteres');
            isValid = false;
        }

        if (!email || !Utils.isValidEmail(email)) {
            this.showFieldError('email', 'Email deve ter um formato válido');
            isValid = false;
        }

        if (!role) {
            this.showFieldError('role', 'Selecione sua área de atuação');
            isValid = false;
        }

        return isValid;
    },

    validateField(field) {
        const value = field.value.trim();

        switch (field.id) {
            case 'name':
                if (!value || value.length < 2) {
                    this.showFieldError('name', 'Nome deve ter pelo menos 2 caracteres');
                    return false;
                }
                break;
            case 'email':
                if (!value || !Utils.isValidEmail(value)) {
                    this.showFieldError('email', 'Email deve ter um formato válido');
                    return false;
                }
                break;
            case 'role':
                if (!value) {
                    this.showFieldError('role', 'Selecione sua área de atuação');
                    return false;
                }
                break;
        }

        this.clearFieldError(field.id);
        return true;
    },

    showFieldError(fieldId, message) {
        const field = this.form.querySelector(`#${fieldId}`);
        const existingError = field.parentNode.querySelector('.field-error');

        if (existingError) {
            existingError.textContent = message;
            return;
        }

        const errorElement = document.createElement('div');
        errorElement.className = 'field-error text-red-500 text-sm mt-1';
        errorElement.textContent = message;

        field.parentNode.appendChild(errorElement);
        field.classList.add('border-red-300', 'focus:border-red-500', 'focus:ring-red-200');
    },

    clearFieldError(fieldId) {
        const fieldElement = typeof fieldId === 'string'
            ? this.form.querySelector(`#${fieldId}`)
            : fieldId;

        const errorElement = fieldElement.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }

        fieldElement.classList.remove('border-red-300', 'focus:border-red-500', 'focus:ring-red-200');
    },

    setLoading(loading) {
        AppState.isLoading = loading;

        if (loading) {
            this.submitButton.disabled = true;
            this.submitButton.classList.add('btn-loading');
            this.submitButton.innerHTML = '<span class="loading-spinner mr-2"></span>Enviando...';
        } else {
            this.submitButton.disabled = false;
            this.submitButton.classList.remove('btn-loading');
            this.submitButton.innerHTML = '🚀 Quero Acesso Antecipado';
        }
    },

    showSuccess() {
        this.form.style.display = 'none';
        this.successMessage.classList.remove('hidden');

        // Add success animation
        this.successMessage.style.opacity = '0';
        this.successMessage.style.transform = 'scale(0.95)';

        setTimeout(() => {
            this.successMessage.style.opacity = '1';
            this.successMessage.style.transform = 'scale(1)';
            this.successMessage.style.transition = 'all 0.3s ease';
        }, 100);

        Utils.showToast('Perfeito! Você está na lista de espera! 🎉', 'success');
    },

    updateWaitlistCount() {
        AppState.waitlistCount += 1;
        const counter = document.getElementById('waitlist-count');
        if (counter) {
            AnimationController.animateCounter(counter,
                AppState.waitlistCount - 1,
                AppState.waitlistCount,
                500
            );
        }
    }
};

// FAQ functionality
const FAQ = {
    init() {
        // FAQ toggle is handled by inline onclick for simplicity
        // But we can enhance it here if needed
        this.setupKeyboardNavigation();
    },

    setupKeyboardNavigation() {
        const faqButtons = document.querySelectorAll('.faq-question');

        faqButtons.forEach(button => {
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });
        });
    }
};

// Navigation enhancements
const Navigation = {
    init() {
        this.setupSmoothScroll();
        this.setupNavbarBehavior();
        this.setupMobileMenu();
    },

    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);

                if (targetElement) {
                    const offsetTop = targetElement.offsetTop - LANDING_CONFIG.SCROLL_OFFSET;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });

                    Utils.trackEvent('navigation_click', { target: targetId });
                }
            });
        });
    },

    setupNavbarBehavior() {
        let lastScrollY = window.scrollY;
        const navbar = document.querySelector('nav');

        const handleScroll = Utils.throttle(() => {
            const currentScrollY = window.scrollY;

            // Add shadow when scrolled
            if (currentScrollY > 10) {
                navbar.classList.add('shadow-lg');
            } else {
                navbar.classList.remove('shadow-lg');
            }

            lastScrollY = currentScrollY;
        }, 16);

        window.addEventListener('scroll', handleScroll);
    },

    setupMobileMenu() {
        // Placeholder for mobile menu functionality
        // Add if needed based on design requirements
    }
};

// Performance monitoring
const PerformanceMonitor = {
    init() {
        this.measurePageLoad();
        this.setupCoreWebVitals();
    },

    measurePageLoad() {
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            Utils.trackEvent('page_load_time', { load_time: loadTime });
        });
    },

    setupCoreWebVitals() {
        // This would integrate with real performance monitoring
        // For now, just log to console
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    console.log('Performance entry:', entry);
                });
            });

            observer.observe({ entryTypes: ['navigation', 'paint'] });
        }
    }
};

// Main application initialization
class LandingPageApp {
    constructor() {
        this.isInitialized = false;
    }

    async init() {
        if (this.isInitialized) return;

        try {
            // Initialize app state
            AppState.userLocation = await Utils.getUserLocation();

            // Check if user already submitted
            AppState.hasSubmitted = localStorage.getItem('symplifika_waitlist_submitted') === 'true';

            // Initialize components
            AnimationController.init();
            WaitlistForm.init();
            FAQ.init();
            Navigation.init();
            PerformanceMonitor.init();

            // Setup global event listeners
            this.setupGlobalEvents();

            // Track page view
            Utils.trackEvent('page_view', {
                page: 'landing_page',
                referrer: document.referrer || 'direct',
                user_agent: navigator.userAgent
            });

            this.isInitialized = true;
            console.log('Symplifika Landing Page initialized successfully');

        } catch (error) {
            console.error('Failed to initialize landing page:', error);
        }
    }

    setupGlobalEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                Utils.trackEvent('page_visible');
            } else {
                Utils.trackEvent('page_hidden');
            }
        });

        // Handle errors
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            Utils.trackEvent('javascript_error', {
                message: e.error?.message || 'Unknown error',
                filename: e.filename,
                line: e.lineno
            });
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            Utils.trackEvent('promise_rejection', {
                reason: e.reason?.toString() || 'Unknown reason'
            });
        });
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new LandingPageApp();
    app.init();
});

// Export for testing or external access
window.SymplifIkaLanding = {
    app: LandingPageApp,
    utils: Utils,
    state: AppState
};
