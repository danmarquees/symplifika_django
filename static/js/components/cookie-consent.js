/**
 * Cookie Consent Management System
 * Gerencia o consentimento de cookies do usuário
 */

class CookieConsent {
    constructor() {
        this.cookieName = 'symplifika_cookie_consent';
        this.cookieExpiry = 365; // dias
        this.consentData = this.getConsentData();
        
        // Elementos DOM
        this.popup = null;
        this.modal = null;
        this.elements = {};
        
        this.init();
    }

    init() {
        // Aguarda o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.findElements();
        this.bindEvents();
        this.checkConsentStatus();
    }

    findElements() {
        this.popup = document.getElementById('cookieConsent');
        this.modal = document.getElementById('cookieSettingsModal');
        
        if (!this.popup || !this.modal) {
            console.warn('Cookie consent elements not found');
            return;
        }

        // Elementos do popup
        this.elements = {
            acceptBtn: document.getElementById('cookieAccept'),
            rejectBtn: document.getElementById('cookieReject'),
            settingsBtn: document.getElementById('cookieSettings'),
            
            // Modal elements
            closeModalBtn: document.getElementById('closeSettingsModal'),
            saveSettingsBtn: document.getElementById('saveSettings'),
            acceptAllSettingsBtn: document.getElementById('acceptAllSettings'),
            rejectAllSettingsBtn: document.getElementById('rejectAllSettings'),
            
            // Checkboxes
            essentialCookies: document.getElementById('essentialCookies'),
            analyticsCookies: document.getElementById('analyticsCookies'),
            marketingCookies: document.getElementById('marketingCookies'),
            functionalCookies: document.getElementById('functionalCookies')
        };
    }

    bindEvents() {
        if (!this.popup || !this.modal) return;

        // Popup events
        this.elements.acceptBtn?.addEventListener('click', () => this.acceptAll());
        this.elements.rejectBtn?.addEventListener('click', () => this.rejectAll());
        this.elements.settingsBtn?.addEventListener('click', () => this.openSettings());

        // Modal events
        this.elements.closeModalBtn?.addEventListener('click', () => this.closeSettings());
        this.elements.saveSettingsBtn?.addEventListener('click', () => this.saveCustomSettings());
        this.elements.acceptAllSettingsBtn?.addEventListener('click', () => this.acceptAllFromModal());
        this.elements.rejectAllSettingsBtn?.addEventListener('click', () => this.rejectAllFromModal());

        // Close modal on background click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeSettings();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (!this.modal.classList.contains('hidden')) {
                    this.closeSettings();
                }
            }
        });
    }

    checkConsentStatus() {
        if (!this.consentData) {
            this.showPopup();
        } else {
            this.applyConsentSettings();
        }
    }

    showPopup() {
        if (this.popup) {
            this.popup.classList.remove('hidden');
            
            // Focus management for accessibility
            setTimeout(() => {
                this.elements.acceptBtn?.focus();
            }, 100);
        }
    }

    hidePopup() {
        if (this.popup) {
            this.popup.classList.add('hiding');
            setTimeout(() => {
                this.popup.classList.add('hidden');
                this.popup.classList.remove('hiding');
            }, 300);
        }
    }

    openSettings() {
        if (this.modal) {
            // Load current settings into checkboxes
            this.loadCurrentSettings();
            this.modal.classList.remove('hidden');
            
            // Focus management
            setTimeout(() => {
                this.elements.closeModalBtn?.focus();
            }, 100);
        }
    }

    closeSettings() {
        if (this.modal) {
            this.modal.classList.add('hidden');
        }
    }

    loadCurrentSettings() {
        const consent = this.consentData || {};
        
        // Essential cookies are always enabled
        if (this.elements.essentialCookies) {
            this.elements.essentialCookies.checked = true;
        }
        
        if (this.elements.analyticsCookies) {
            this.elements.analyticsCookies.checked = consent.analytics || false;
        }
        
        if (this.elements.marketingCookies) {
            this.elements.marketingCookies.checked = consent.marketing || false;
        }
        
        if (this.elements.functionalCookies) {
            this.elements.functionalCookies.checked = consent.functional || false;
        }
    }

    acceptAll() {
        const consent = {
            essential: true,
            analytics: true,
            marketing: true,
            functional: true,
            timestamp: new Date().toISOString()
        };
        
        this.saveConsent(consent);
        this.hidePopup();
        this.applyConsentSettings();
        this.triggerConsentEvent('accepted_all');
    }

    rejectAll() {
        const consent = {
            essential: true,
            analytics: false,
            marketing: false,
            functional: false,
            timestamp: new Date().toISOString()
        };
        
        this.saveConsent(consent);
        this.hidePopup();
        this.applyConsentSettings();
        this.triggerConsentEvent('rejected_all');
    }

    acceptAllFromModal() {
        this.acceptAll();
        this.closeSettings();
    }

    rejectAllFromModal() {
        this.rejectAll();
        this.closeSettings();
    }

    saveCustomSettings() {
        const consent = {
            essential: true, // Always true
            analytics: this.elements.analyticsCookies?.checked || false,
            marketing: this.elements.marketingCookies?.checked || false,
            functional: this.elements.functionalCookies?.checked || false,
            timestamp: new Date().toISOString()
        };
        
        this.saveConsent(consent);
        this.hidePopup();
        this.closeSettings();
        this.applyConsentSettings();
        this.triggerConsentEvent('custom_settings');
    }

    saveConsent(consent) {
        this.consentData = consent;
        const cookieValue = JSON.stringify(consent);
        const expiryDate = new Date();
        expiryDate.setTime(expiryDate.getTime() + (this.cookieExpiry * 24 * 60 * 60 * 1000));
        
        document.cookie = `${this.cookieName}=${cookieValue}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
    }

    getConsentData() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === this.cookieName) {
                try {
                    return JSON.parse(decodeURIComponent(value));
                } catch (e) {
                    console.warn('Failed to parse cookie consent data:', e);
                    return null;
                }
            }
        }
        return null;
    }

    applyConsentSettings() {
        if (!this.consentData) return;

        // Apply analytics consent
        if (this.consentData.analytics) {
            this.enableAnalytics();
        } else {
            this.disableAnalytics();
        }

        // Apply marketing consent
        if (this.consentData.marketing) {
            this.enableMarketing();
        } else {
            this.disableMarketing();
        }

        // Apply functional consent
        if (this.consentData.functional) {
            this.enableFunctional();
        } else {
            this.disableFunctional();
        }
    }

    enableAnalytics() {
        // Google Analytics, etc.
        console.log('Analytics cookies enabled');
        
        // Exemplo: Inicializar Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {
                'analytics_storage': 'granted'
            });
        }
    }

    disableAnalytics() {
        console.log('Analytics cookies disabled');
        
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {
                'analytics_storage': 'denied'
            });
        }
    }

    enableMarketing() {
        console.log('Marketing cookies enabled');
        
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {
                'ad_storage': 'granted'
            });
        }
    }

    disableMarketing() {
        console.log('Marketing cookies disabled');
        
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {
                'ad_storage': 'denied'
            });
        }
    }

    enableFunctional() {
        console.log('Functional cookies enabled');
        // Habilitar funcionalidades como chat, preferências, etc.
    }

    disableFunctional() {
        console.log('Functional cookies disabled');
        // Desabilitar funcionalidades não essenciais
    }

    triggerConsentEvent(action) {
        // Disparar evento customizado para analytics
        const event = new CustomEvent('cookieConsentChanged', {
            detail: {
                action: action,
                consent: this.consentData
            }
        });
        document.dispatchEvent(event);
    }

    // Método público para resetar consentimento
    resetConsent() {
        document.cookie = `${this.cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        this.consentData = null;
        this.showPopup();
    }

    // Método público para obter status do consentimento
    getConsent() {
        return this.consentData;
    }

    // Método público para verificar se um tipo específico foi consentido
    hasConsent(type) {
        return this.consentData && this.consentData[type] === true;
    }
}

// Inicializar quando o script carregar
const cookieConsent = new CookieConsent();

// Expor globalmente para uso em outros scripts
window.CookieConsent = cookieConsent;

// Event listener para mudanças de consentimento
document.addEventListener('cookieConsentChanged', (e) => {
    console.log('Cookie consent changed:', e.detail);
    
    // Aqui você pode adicionar lógica adicional quando o consentimento mudar
    // Por exemplo, recarregar scripts de analytics, etc.
});
