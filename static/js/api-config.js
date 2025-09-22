/**
 * API Configuration and Utilities for Symplifika Frontend
 * Provides centralized API endpoint management and helper functions
 */

class APIConfig {
    constructor() {
        // Get configuration from Django template context
        this.config = window.apiConfig || {};
        this.baseUrl = this.config.api_base_url || 'http://localhost:8000';
        this.frontendUrl = this.config.frontend_url || 'http://localhost:3000';
        this.endpoints = this.config.endpoints || {};
        this.stripe = this.config.stripe || {};
        this.environment = this.config.environment || {};
    }

    /**
     * Get full API endpoint URL
     * @param {string} category - Endpoint category (auth, shortcuts, payments)
     * @param {string} endpoint - Specific endpoint name
     * @param {Object} params - URL parameters to replace
     * @returns {string} Full endpoint URL
     */
    getEndpoint(category, endpoint, params = {}) {
        try {
            let url = this.endpoints[category][endpoint];
            
            // Replace URL parameters
            Object.keys(params).forEach(key => {
                url = url.replace(`{${key}}`, params[key]);
            });
            
            return this.baseUrl + url;
        } catch (error) {
            console.error(`Endpoint ${category}.${endpoint} not found`, error);
            return null;
        }
    }

    /**
     * Get Stripe configuration
     * @returns {Object} Stripe configuration
     */
    getStripeConfig() {
        return this.stripe;
    }

    /**
     * Check if Stripe is configured
     * @returns {boolean} True if Stripe is configured
     */
    isStripeConfigured() {
        return this.stripe.configured || false;
    }

    /**
     * Get environment information
     * @returns {Object} Environment configuration
     */
    getEnvironment() {
        return this.environment;
    }

    /**
     * Check if running in production
     * @returns {boolean} True if production environment
     */
    isProduction() {
        return this.environment.is_production || false;
    }

    /**
     * Get CSRF token from cookies
     * @returns {string} CSRF token
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Make authenticated API request
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @returns {Promise} Fetch promise
     */
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            credentials: 'include',
        };

        // Merge options
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Show notification to user using global Toast system
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info, warning)
     */
    showNotification(message, type = 'info') {
        // Use global Toast system if available
        if (window.Toast) {
            return window.Toast.show({
                type: type,
                message: message,
                duration: type === 'error' ? 8000 : 5000
            });
        }
        
        // Fallback to console log
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    /**
     * Handle API errors consistently
     * @param {Error} error - Error object
     * @param {string} context - Context where error occurred
     */
    handleError(error, context = 'API request') {
        console.error(`${context} failed:`, error);
        
        let message = 'Ocorreu um erro inesperado. Tente novamente.';
        
        if (error.message.includes('401')) {
            message = 'Sessão expirada. Faça login novamente.';
            // Redirect to login if needed
            if (!window.location.pathname.includes('/login/')) {
                window.location.href = '/auth/login/';
            }
        } else if (error.message.includes('403')) {
            message = 'Você não tem permissão para esta ação.';
        } else if (error.message.includes('404')) {
            message = 'Recurso não encontrado.';
        } else if (error.message.includes('500')) {
            message = 'Erro interno do servidor. Tente novamente mais tarde.';
        }
        
        this.showNotification(message, 'error');
    }
}

// Create global instance
window.apiConfig = new APIConfig();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIConfig;
}
