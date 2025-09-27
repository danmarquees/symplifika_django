// Symplifika Landing Page Configuration
// Este arquivo centraliza todas as configurações da landing page

const LANDING_CONFIG = {
    // Configurações da API
    API: {
        BASE_URL: window.location.origin,
        ENDPOINTS: {
            WAITLIST_SUBMIT: '/api/waitlist/submit/',
            ANALYTICS_TRACK: '/api/analytics/track/',
            CONTACT_FORM: '/api/contact/submit/',
            NEWSLETTER: '/api/newsletter/subscribe/'
        },
        TIMEOUT: 10000, // 10 segundos
        RETRY_ATTEMPTS: 3
    },

    // Configurações de Analytics
    ANALYTICS: {
        GOOGLE_ANALYTICS_ID: 'GA_TRACKING_ID', // Substitua pelo ID real
        GOOGLE_TAG_MANAGER_ID: 'GTM-XXXXXXX', // Substitua pelo ID real
        FACEBOOK_PIXEL_ID: 'YOUR_PIXEL_ID',
        HOTJAR_ID: 'YOUR_HOTJAR_ID',

        // Eventos customizados
        EVENTS: {
            PAGE_VIEW: 'page_view',
            FORM_START: 'form_start',
            FORM_SUBMIT: 'form_submit',
            FORM_SUCCESS: 'form_success',
            FORM_ERROR: 'form_error',
            CTA_CLICK: 'cta_click',
            SCROLL_DEPTH: 'scroll_depth',
            TIME_ON_PAGE: 'time_on_page',
            FAQ_OPEN: 'faq_open',
            SOCIAL_SHARE: 'social_share'
        }
    },

    // Configurações da UI
    UI: {
        ANIMATION_DURATION: 300,
        SCROLL_OFFSET: 100,
        TOAST_DURATION: 5000,
        LOADING_MIN_TIME: 1000, // Tempo mínimo de loading para UX

        // Breakpoints responsivos
        BREAKPOINTS: {
            MOBILE: 768,
            TABLET: 1024,
            DESKTOP: 1200
        },

        // Cores do tema
        THEME: {
            PRIMARY: '#00c853',
            SECONDARY: '#00ff57',
            ACCENT: '#4caf50',
            DARK: '#1a1a1a',
            LIGHT: '#f8f9fa',
            SUCCESS: '#10b981',
            WARNING: '#f59e0b',
            ERROR: '#ef4444',
            INFO: '#3b82f6'
        }
    },

    // Configurações do formulário
    FORM: {
        VALIDATION: {
            NAME_MIN_LENGTH: 2,
            NAME_MAX_LENGTH: 100,
            EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            REQUIRED_FIELDS: ['name', 'email', 'role']
        },

        // Mensagens de validação
        MESSAGES: {
            REQUIRED: 'Este campo é obrigatório',
            EMAIL_INVALID: 'Por favor, insira um email válido',
            NAME_TOO_SHORT: 'Nome deve ter pelo menos 2 caracteres',
            NAME_TOO_LONG: 'Nome deve ter no máximo 100 caracteres',
            GENERIC_ERROR: 'Ops! Algo deu errado. Tente novamente.',
            SUCCESS: 'Perfeito! Você está na nossa lista de espera! 🎉',
            ALREADY_SUBMITTED: 'Você já está na nossa lista de espera!'
        },

        // Opções do campo "área de atuação"
        ROLE_OPTIONS: [
            { value: 'marketing', label: 'Marketing' },
            { value: 'vendas', label: 'Vendas' },
            { value: 'atendimento', label: 'Atendimento ao Cliente' },
            { value: 'rh', label: 'Recursos Humanos' },
            { value: 'desenvolvedor', label: 'Desenvolvimento' },
            { value: 'design', label: 'Design' },
            { value: 'gestao', label: 'Gestão/Liderança' },
            { value: 'freelancer', label: 'Freelancer' },
            { value: 'estudante', label: 'Estudante' },
            { value: 'outro', label: 'Outro' }
        ]
    },

    // Configurações de Social Proof
    SOCIAL_PROOF: {
        INITIAL_COUNT: 127, // Contador inicial da lista de espera
        INCREMENT_RANGE: [1, 3], // Range de incremento aleatório
        UPDATE_INTERVAL: [2000, 5000], // Intervalo entre atualizações (ms)
        MAX_COUNT: 1000, // Limite máximo para o contador

        // Testimonials rotativos
        TESTIMONIALS: [
            {
                name: "Carlos Silva",
                role: "Gerente de Marketing",
                avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2300c853' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.51.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72zm11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33C4.62 15.49 4 13.82 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.49-1.64 4.83zM12 6c-1.94 0-3.5 1.56-3.5 3.5S10.06 13 12 13s3.5-1.56 3.5-3.5S13.94 6 12 6zm0 5c-.83 0-1.5-.67-1.5-1.5S11.17 8 12 8s1.5.67 1.5 1.5S12.83 11 12 11z'/%3E%3C/svg%3E",
                text: "Finalmente uma ferramenta que vai economizar horas do meu dia!"
            },
            {
                name: "Ana Costa",
                role: "Desenvolvedora Frontend",
                avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2300ff57' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.51.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72zm11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33C4.62 15.49 4 13.82 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.49-1.64 4.83zM12 6c-1.94 0-3.5 1.56-3.5 3.5S10.06 13 12 13s3.5-1.56 3.5-3.5S13.94 6 12 6zm0 5c-.83 0-1.5-.67-1.5-1.5S11.17 8 12 8s1.5.67 1.5 1.5S12.83 11 12 11z'/%3E%3C/svg%3E",
                text: "A IA integrada parece incrível! Mal posso esperar para testar."
            },
            {
                name: "Rafael Oliveira",
                role: "Consultor de Vendas",
                avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234caf50' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.51.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72zm11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33C4.62 15.49 4 13.82 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.49-1.64 4.83zM12 6c-1.94 0-3.5 1.56-3.5 3.5S10.06 13 12 13s3.5-1.56 3.5-3.5S13.94 6 12 6zm0 5c-.83 0-1.5-.67-1.5-1.5S11.17 8 12 8s1.5.67 1.5 1.5S12.83 11 12 11z'/%3E%3C/svg%3E",
                text: "Isso vai mudar completamente meu fluxo de trabalho!"
            }
        ]
    },

    // Configurações de Performance
    PERFORMANCE: {
        LAZY_LOAD_THRESHOLD: 100, // px antes de carregar imagem
        DEBOUNCE_DELAY: 300, // ms para eventos debounced
        THROTTLE_DELAY: 16, // ms para scroll events (~60fps)
        INTERSECTION_THRESHOLD: 0.1, // 10% visível para trigger
        INTERSECTION_ROOT_MARGIN: '0px 0px -50px 0px'
    },

    // Configurações de Segurança
    SECURITY: {
        CSRF_TOKEN_NAME: 'csrfmiddlewaretoken',
        RATE_LIMIT: {
            FORM_SUBMISSIONS: 3, // máximo por minuto
            API_CALLS: 60 // máximo por minuto
        },
        ALLOWED_DOMAINS: [
            'symplifika.com',
            'www.symplifika.com',
            'localhost',
            '127.0.0.1'
        ]
    },

    // Configurações de Desenvolvimento
    DEV: {
        DEBUG: window.location.hostname === 'localhost' ||
               window.location.hostname === '127.0.0.1',
        MOCK_API: true, // Usar mock API em desenvolvimento
        CONSOLE_LOGS: true,
        PERFORMANCE_MONITORING: true,
        ERROR_REPORTING: true
    },

    // URLs e Links Externos
    EXTERNAL_LINKS: {
        SOCIAL_MEDIA: {
            FACEBOOK: 'https://facebook.com/symplifika',
            TWITTER: 'https://twitter.com/symplifika',
            LINKEDIN: 'https://linkedin.com/company/symplifika',
            INSTAGRAM: 'https://instagram.com/symplifika'
        },
        LEGAL: {
            PRIVACY_POLICY: '/privacy-policy/',
            TERMS_OF_SERVICE: '/terms-of-service/',
            COOKIE_POLICY: '/cookie-policy/'
        },
        SUPPORT: {
            HELP_CENTER: '/help/',
            CONTACT: '/contact/',
            FAQ: '#faq'
        }
    },

    // Configurações de Email Marketing
    EMAIL_MARKETING: {
        PROVIDER: 'mailchimp', // ou 'sendgrid', 'mailgun', etc.
        LIST_ID: 'YOUR_MAILCHIMP_LIST_ID',
        WELCOME_SERIES: true,
        DOUBLE_OPT_IN: true,
        TAGS: {
            WAITLIST: 'waitlist',
            EARLY_ACCESS: 'early-access',
            BETA_TESTER: 'beta-tester'
        }
    },

    // Mensagens e Copy
    COPY: {
        HERO: {
            BADGE_TEXT: 'Em desenvolvimento • Lançamento em breve',
            MAIN_TITLE: 'Automações fáceis_e_rápidas no seu dia-a-dia',
            SUBTITLE: 'Descubra a plataforma de automação de texto com IA integrada que vai revolucionar sua produtividade. Crie atalhos inteligentes, economize tempo e trabalhe de forma mais eficiente.',
            CTA_PRIMARY: '🚀 Quero Acesso Antecipado',
            CTA_SECONDARY: 'Ver Demonstração'
        },
        SOCIAL_PROOF: {
            COUNTER_TEXT: 'pessoas já na lista de espera',
            BENEFITS: [
                { icon: '🎁', title: 'Acesso Gratuito', subtitle: '30 dias grátis para testar' },
                { icon: '💰', title: 'Desconto Exclusivo', subtitle: '50% OFF no primeiro ano' },
                { icon: '🏆', title: 'Suporte VIP', subtitle: 'Atendimento prioritário' }
            ]
        }
    }
};

// Exportar configuração
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LANDING_CONFIG;
} else if (typeof window !== 'undefined') {
    window.LANDING_CONFIG = LANDING_CONFIG;
}

// Função para obter configuração com fallback
function getConfig(path, fallback = null) {
    return path.split('.').reduce((obj, key) => {
        return (obj && obj[key] !== undefined) ? obj[key] : fallback;
    }, LANDING_CONFIG);
}

// Função para detectar ambiente
function getEnvironment() {
    const hostname = window.location.hostname;

    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('.local')) {
        return 'development';
    } else if (hostname.includes('staging') || hostname.includes('dev')) {
        return 'staging';
    } else {
        return 'production';
    }
}

// Função para configurar baseado no ambiente
function setupEnvironment() {
    const env = getEnvironment();

    switch (env) {
        case 'development':
            LANDING_CONFIG.DEV.DEBUG = true;
            LANDING_CONFIG.DEV.MOCK_API = true;
            LANDING_CONFIG.ANALYTICS.GOOGLE_ANALYTICS_ID = 'GA_TRACKING_ID_DEV';
            break;

        case 'staging':
            LANDING_CONFIG.DEV.DEBUG = true;
            LANDING_CONFIG.DEV.MOCK_API = false;
            LANDING_CONFIG.ANALYTICS.GOOGLE_ANALYTICS_ID = 'GA_TRACKING_ID_STAGING';
            break;

        case 'production':
            LANDING_CONFIG.DEV.DEBUG = false;
            LANDING_CONFIG.DEV.MOCK_API = false;
            LANDING_CONFIG.ANALYTICS.GOOGLE_ANALYTICS_ID = 'GA_TRACKING_ID_PROD';
            break;
    }
}

// Configurar ambiente automaticamente
setupEnvironment();

// Função para validar configuração
function validateConfig() {
    const required = [
        'API.BASE_URL',
        'API.ENDPOINTS.WAITLIST_SUBMIT',
        'FORM.VALIDATION.REQUIRED_FIELDS'
    ];

    const missing = required.filter(path => !getConfig(path));

    if (missing.length > 0) {
        console.warn('Missing required configuration:', missing);
    }

    return missing.length === 0;
}

// Validar configuração na inicialização
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        if (LANDING_CONFIG.DEV.DEBUG) {
            console.log('Landing Page Config:', LANDING_CONFIG);
            validateConfig();
        }
    });
}
