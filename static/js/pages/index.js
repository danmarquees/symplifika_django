// Index Page JavaScript Functionality

document.addEventListener("DOMContentLoaded", function () {
    // Initialize index page functionality
    IndexPage.init();
});

const IndexPage = {
    init() {
        this.setupSmoothScroll();
        this.setupParallaxEffect();
        this.setupIntersectionObserver();
        this.setupCounterAnimations();
        this.setupScrollIndicator();
        this.setupCTAAnimations();
    },

    // Smooth scroll for anchor links
    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
            anchor.addEventListener("click", function (e) {
                e.preventDefault();
                const target = document.querySelector(
                    this.getAttribute("href"),
                );
                if (target) {
                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                    });
                }
            });
        });
    },

    // Parallax effect for hero section
    setupParallaxEffect() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }

        const heroSection = document.querySelector("section.hero-parallax, section:first-of-type");
        if (!heroSection) return;

        const throttledScroll = Utils.throttle(() => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        }, 16);

        window.addEventListener("scroll", throttledScroll);
    },

    // Intersection Observer for animations
    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: "0px 0px -50px 0px",
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("animate-fade-in");

                    // Special handling for feature cards
                    if (entry.target.classList.contains("card")) {
                        setTimeout(() => {
                            entry.target.classList.add("feature-card");
                        }, 100);
                    }

                    // Trigger counter animation for stats
                    if (entry.target.classList.contains("stat-number")) {
                        this.animateCounter(entry.target);
                    }

                    // Unobserve after animation
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll(".card, .stat-number, .feature-icon").forEach((element) => {
            observer.observe(element);
        });
    },

    // Counter animation for statistics
    animateCounter(element) {
        const finalValue = parseInt(element.textContent.replace(/\D/g, ''));
        const duration = 2000;
        const start = Date.now();

        const updateCounter = () => {
            const elapsed = Date.now() - start;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(finalValue * easeOutQuart);

            element.textContent = currentValue + (element.textContent.includes('+') ? '+' : '');

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = element.dataset.originalText || element.textContent;
            }
        };

        // Store original text
        element.dataset.originalText = element.textContent;
        requestAnimationFrame(updateCounter);
    },

    // Setup scroll indicator
    setupScrollIndicator() {
        const scrollIndicator = document.querySelector('.scroll-indicator, .animate-bounce svg');
        if (!scrollIndicator) return;

        const handleScroll = () => {
            const scrolled = window.pageYOffset;
            const windowHeight = window.innerHeight;

            if (scrolled > windowHeight * 0.3) {
                scrollIndicator.style.opacity = '0';
            } else {
                scrollIndicator.style.opacity = '1';
            }
        };

        window.addEventListener('scroll', Utils.throttle(handleScroll, 100));
    },

    // Setup CTA button animations
    setupCTAAnimations() {
        const ctaButtons = document.querySelectorAll('.btn');

        ctaButtons.forEach(button => {
            // Add shimmer effect class
            button.classList.add('cta-button');

            // Add click ripple effect
            button.addEventListener('click', function(e) {
                const rect = this.getBoundingClientRect();
                const ripple = document.createElement('span');
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;

                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);

                setTimeout(() => ripple.remove(), 600);
            });
        });

        // Add ripple animation CSS
        if (!document.querySelector('#ripple-style')) {
            const style = document.createElement('style');
            style.id = 'ripple-style';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    },

    // Demo credentials helper
    setupDemoCredentials() {
        window.fillDemoCredentials = function() {
            const usernameField = document.querySelector('input[name="username"]');
            const passwordField = document.querySelector('input[name="password"]');

            if (usernameField) usernameField.value = 'demo';
            if (passwordField) passwordField.value = 'demo123';

            // Add visual feedback
            Toast.info('Credenciais de demonstração preenchidas');
        };
    },

    // Background decoration animation
    setupBackgroundDecorations() {
        const decorations = document.querySelectorAll('.bg-decoration, .absolute');

        decorations.forEach((decoration, index) => {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                return;
            }

            // Add floating animation with different delays
            decoration.style.animationDelay = `${index * 0.5}s`;
            decoration.classList.add('bg-decoration');
        });
    }
};

// Utility functions specific to index page
const IndexUtils = {
    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    // Get scroll percentage
    getScrollPercentage() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        return (scrollTop / docHeight) * 100;
    },

    // Smooth scroll to element
    scrollToElement(selector, offset = 0) {
        const element = document.querySelector(selector);
        if (element) {
            const targetPosition = element.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }
};

// Performance optimization: reduce animations on mobile
if (window.innerWidth < 768) {
    document.documentElement.style.setProperty('--animation-duration', '0.2s');
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    // Remove any active intervals or timeouts
    document.querySelectorAll('.animate-fade-in, .animate-slide-in').forEach(el => {
        el.style.animation = 'none';
    });
});

// Export for global access if needed
window.IndexPage = IndexPage;
window.IndexUtils = IndexUtils;
