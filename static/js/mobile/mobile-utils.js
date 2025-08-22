/**
 * Symplifika Mobile Utilities
 * Enhanced mobile-specific functionality and utilities
 */

class MobileUtils {
    constructor() {
        this.isMobile = window.innerWidth < 768;
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        this.lastScrollY = 0;
        this.isScrollingDown = false;
        this.scrollThreshold = 10;

        this.init();
    }

    init() {
        this.detectDevice();
        this.handleViewportChanges();
        this.setupScrollBehavior();
        this.setupTouchFeedback();
        this.setupSwipeGestures();
        this.preventZoomOnDoubleTap();
        this.handleOrientationChange();
    }

    /**
     * Detect device capabilities and set CSS classes
     */
    detectDevice() {
        const html = document.documentElement;

        if (this.isMobile) {
            html.classList.add('is-mobile');
        } else {
            html.classList.add('is-desktop');
        }

        if (this.isTouch) {
            html.classList.add('is-touch');
        } else {
            html.classList.add('is-mouse');
        }

        // Detect iOS
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            html.classList.add('is-ios');
        }

        // Detect Android
        if (/Android/.test(navigator.userAgent)) {
            html.classList.add('is-android');
        }
    }

    /**
     * Handle viewport size changes
     */
    handleViewportChanges() {
        let resizeTimer;

        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const wasMobile = this.isMobile;
                this.isMobile = window.innerWidth < 768;

                if (wasMobile !== this.isMobile) {
                    this.detectDevice();
                    this.handleBreakpointChange();
                }
            }, 250);
        });
    }

    /**
     * Handle breakpoint changes (mobile to desktop or vice versa)
     */
    handleBreakpointChange() {
        // Close mobile-specific elements when switching to desktop
        if (!this.isMobile) {
            this.closeMobileMenu();
            this.closeMobileSidebar();
        }

        // Trigger custom event
        window.dispatchEvent(new CustomEvent('breakpointChange', {
            detail: { isMobile: this.isMobile }
        }));
    }

    /**
     * Setup enhanced scroll behavior for mobile
     */
    setupScrollBehavior() {
        let ticking = false;

        const updateScrollDirection = () => {
            const currentScrollY = window.pageYOffset;

            if (Math.abs(currentScrollY - this.lastScrollY) > this.scrollThreshold) {
                this.isScrollingDown = currentScrollY > this.lastScrollY;
                this.lastScrollY = currentScrollY;

                // Trigger scroll direction change event
                window.dispatchEvent(new CustomEvent('scrollDirectionChange', {
                    detail: {
                        isScrollingDown: this.isScrollingDown,
                        scrollY: currentScrollY
                    }
                }));
            }

            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollDirection);
                ticking = true;
            }
        }, { passive: true });
    }

    /**
     * Add touch feedback to interactive elements
     */
    setupTouchFeedback() {
        if (!this.isTouch) return;

        const addTouchFeedback = (element) => {
            let touchStartTime;

            element.addEventListener('touchstart', (e) => {
                touchStartTime = Date.now();
                element.classList.add('touch-active');
            }, { passive: true });

            element.addEventListener('touchend', () => {
                const touchDuration = Date.now() - touchStartTime;

                setTimeout(() => {
                    element.classList.remove('touch-active');
                }, Math.max(0, 150 - touchDuration));
            }, { passive: true });

            element.addEventListener('touchcancel', () => {
                element.classList.remove('touch-active');
            }, { passive: true });
        };

        // Apply to buttons and interactive elements
        const interactiveSelector = '.btn, .nav-item, .sidebar-item, [role="button"], button, a, .interactive';
        document.querySelectorAll(interactiveSelector).forEach(addTouchFeedback);

        // Observer for dynamically added elements
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.matches && node.matches(interactiveSelector)) {
                            addTouchFeedback(node);
                        }
                        node.querySelectorAll && node.querySelectorAll(interactiveSelector).forEach(addTouchFeedback);
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    /**
     * Setup swipe gestures for mobile navigation
     */
    setupSwipeGestures() {
        if (!this.isTouch) return;

        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        let isSwiping = false;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
            isSwiping = true;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!isSwiping) return;

            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!isSwiping) return;

            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;

            this.handleSwipe(touchStartX, touchStartY, touchEndX, touchEndY);
            isSwiping = false;
        }, { passive: true });
    }

    /**
     * Handle swipe gestures
     */
    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const threshold = 50;
        const restraint = 100;

        // Right swipe (open sidebar from left edge)
        if (deltaX > threshold && Math.abs(deltaY) < restraint && startX < 30) {
            this.openMobileSidebar();
        }
        // Left swipe (close sidebar)
        else if (deltaX < -threshold && Math.abs(deltaY) < restraint) {
            this.closeMobileSidebar();
        }
        // Up swipe (hide mobile header on scroll)
        else if (deltaY < -threshold && Math.abs(deltaX) < restraint) {
            this.hideMobileHeader();
        }
        // Down swipe (show mobile header)
        else if (deltaY > threshold && Math.abs(deltaX) < restraint && window.pageYOffset === 0) {
            this.showMobileHeader();
        }
    }

    /**
     * Prevent zoom on double tap for better UX
     */
    preventZoomOnDoubleTap() {
        let lastTouchEnd = 0;

        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, { passive: false });
    }

    /**
     * Handle orientation changes
     */
    handleOrientationChange() {
        window.addEventListener('orientationchange', () => {
            // Fix viewport issues on mobile
            setTimeout(() => {
                window.scrollTo(0, 0);
                this.updateViewportHeight();
            }, 500);
        });

        // Handle screen size changes (keyboard show/hide on mobile)
        this.updateViewportHeight();
        window.addEventListener('resize', () => {
            this.updateViewportHeight();
        });
    }

    /**
     * Update viewport height to handle mobile browser chrome
     */
    updateViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    /**
     * Close mobile menu
     */
    closeMobileMenu() {
        const mobileMenu = document.getElementById('mobile-menu');
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const hamburgerIcon = document.querySelector('.hamburger-icon');
        const closeIcon = document.querySelector('.close-icon');

        if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
            document.body.style.overflow = '';

            if (hamburgerIcon && closeIcon) {
                hamburgerIcon.classList.remove('hidden');
                closeIcon.classList.add('hidden');
            }

            if (mobileMenuButton) {
                mobileMenuButton.setAttribute('aria-expanded', 'false');
            }
        }
    }

    /**
     * Open mobile sidebar
     */
    openMobileSidebar() {
        const sidebar = document.getElementById('app-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        if (sidebar && sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.remove('-translate-x-full');
            if (backdrop) {
                backdrop.classList.remove('hidden');
            }
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Close mobile sidebar
     */
    closeMobileSidebar() {
        const sidebar = document.getElementById('app-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        if (sidebar && !sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.add('-translate-x-full');
            if (backdrop) {
                backdrop.classList.add('hidden');
            }
            document.body.style.overflow = '';
        }
    }

    /**
     * Hide mobile header on scroll down
     */
    hideMobileHeader() {
        const header = document.querySelector('.mobile-header');
        if (header) {
            header.classList.add('header-hidden');
        }
    }

    /**
     * Show mobile header
     */
    showMobileHeader() {
        const header = document.querySelector('.mobile-header');
        if (header) {
            header.classList.remove('header-hidden');
        }
    }

    /**
     * Safe area insets support (for notch devices)
     */
    setSafeAreaInsets() {
        const root = document.documentElement;

        // Set CSS custom properties for safe areas
        if (CSS.supports('padding: env(safe-area-inset-top)')) {
            root.style.setProperty('--safe-area-top', 'env(safe-area-inset-top)');
            root.style.setProperty('--safe-area-right', 'env(safe-area-inset-right)');
            root.style.setProperty('--safe-area-bottom', 'env(safe-area-inset-bottom)');
            root.style.setProperty('--safe-area-left', 'env(safe-area-inset-left)');
        } else {
            root.style.setProperty('--safe-area-top', '0px');
            root.style.setProperty('--safe-area-right', '0px');
            root.style.setProperty('--safe-area-bottom', '0px');
            root.style.setProperty('--safe-area-left', '0px');
        }
    }

    /**
     * Optimize images for mobile
     */
    optimizeImages() {
        const images = document.querySelectorAll('img[data-mobile-src]');

        images.forEach(img => {
            if (this.isMobile && img.dataset.mobileSrc) {
                img.src = img.dataset.mobileSrc;
            }
        });
    }

    /**
     * Handle mobile-specific form improvements
     */
    improveForms() {
        const inputs = document.querySelectorAll('input, textarea, select');

        inputs.forEach(input => {
            // Prevent zoom on focus for iOS
            if (this.isTouch && input.type !== 'file') {
                input.addEventListener('focus', () => {
                    if (input.style.fontSize !== '16px') {
                        input.dataset.originalFontSize = input.style.fontSize;
                        input.style.fontSize = '16px';
                    }
                });

                input.addEventListener('blur', () => {
                    if (input.dataset.originalFontSize) {
                        input.style.fontSize = input.dataset.originalFontSize;
                    }
                });
            }
        });
    }

    /**
     * Debounce utility function
     */
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
    }

    /**
     * Throttle utility function
     */
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.MobileUtils = new MobileUtils();
});

// Add CSS for touch feedback
const touchStyles = `
    <style>
        .touch-active {
            opacity: 0.7 !important;
            transform: scale(0.98) !important;
            transition: all 0.1s ease-out !important;
        }

        .header-hidden {
            transform: translateY(-100%) !important;
            transition: transform 0.3s ease-in-out !important;
        }

        /* Viewport height fix for mobile browsers */
        .min-h-screen-mobile {
            min-height: 100vh;
            min-height: calc(var(--vh, 1vh) * 100);
        }

        /* Safe area support */
        .safe-area-top {
            padding-top: var(--safe-area-top);
        }

        .safe-area-bottom {
            padding-bottom: var(--safe-area-bottom);
        }

        .safe-area-left {
            padding-left: var(--safe-area-left);
        }

        .safe-area-right {
            padding-right: var(--safe-area-right);
        }

        /* Hide scrollbars on mobile for cleaner look */
        @media (max-width: 767px) {
            .no-scrollbar {
                -ms-overflow-style: none;
                scrollbar-width: none;
            }

            .no-scrollbar::-webkit-scrollbar {
                display: none;
            }
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', touchStyles);
