// Symplifika Service Worker
// Provides offline functionality and caching for better mobile experience

const CACHE_NAME = 'symplifika-v1.0.0';
const STATIC_CACHE_NAME = 'symplifika-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'symplifika-dynamic-v1.0.0';

// Files to cache immediately (App Shell)
const STATIC_ASSETS = [
    '/',
    '/static/css/base.css',
    '/static/css/responsive-mobile.css',
    '/static/css/components/navbar.css',
    '/static/css/components/modal.css',
    '/static/css/components/forms-mobile.css',
    '/static/js/base.js',
    '/static/js/mobile/mobile-utils.js',
    '/static/js/symplifika-base.js',
    '/static/manifest.json',
    '/static/images/favicon.ico',
    'https://cdn.tailwindcss.com',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap'
];

// Pages to cache dynamically
const DYNAMIC_ASSETS = [
    '/dashboard/',
    '/login/',
    '/register/',
    '/help/',
    '/about/',
    '/pricing/'
];

// Network timeout for cache fallback
const NETWORK_TIMEOUT = 3000;

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker');

    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[SW] Static assets cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[SW] Failed to cache static assets:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker');

    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE_NAME &&
                            cacheName !== DYNAMIC_CACHE_NAME &&
                            cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip chrome-extension and other non-http(s) schemes
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Handle different types of requests
    if (isStaticAsset(request)) {
        // Static assets: Cache First strategy
        event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(request)) {
        // API requests: Network First with cache fallback
        event.respondWith(networkFirstWithTimeout(request));
    } else if (isPageRequest(request)) {
        // Page requests: Stale While Revalidate
        event.respondWith(staleWhileRevalidate(request));
    } else {
        // Default: Network with cache fallback
        event.respondWith(networkWithCacheFallback(request));
    }
});

// Cache First Strategy - for static assets
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache first failed:', error);
        return new Response('Asset not available offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Network First with Timeout - for API requests
async function networkFirstWithTimeout(request) {
    try {
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Network timeout')), NETWORK_TIMEOUT)
        );

        const networkResponse = await Promise.race([
            fetch(request),
            timeoutPromise
        ]);

        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', error.message);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        return new Response(
            JSON.stringify({
                error: 'No network connection',
                offline: true,
                message: 'Esta funcionalidade não está disponível offline'
            }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

// Stale While Revalidate - for pages
async function staleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    const cachedResponse = await cache.match(request);

    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch(error => {
        console.log('[SW] Network failed for page:', error.message);
        return null;
    });

    // Return cached version immediately if available, otherwise wait for network
    if (cachedResponse) {
        fetchPromise; // Update cache in background
        return cachedResponse;
    } else {
        const networkResponse = await fetchPromise;
        if (networkResponse) {
            return networkResponse;
        } else {
            return getOfflinePage();
        }
    }
}

// Network with Cache Fallback - default strategy
async function networkWithCacheFallback(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', error.message);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        return getOfflinePage();
    }
}

// Helper function to check if request is for static assets
function isStaticAsset(request) {
    const url = new URL(request.url);
    return url.pathname.includes('/static/') ||
           url.hostname === 'fonts.googleapis.com' ||
           url.hostname === 'fonts.gstatic.com' ||
           url.hostname === 'cdn.tailwindcss.com' ||
           request.destination === 'image' ||
           request.destination === 'style' ||
           request.destination === 'script' ||
           request.destination === 'font';
}

// Helper function to check if request is for API
function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/') ||
           url.pathname.startsWith('/ajax/') ||
           request.headers.get('Content-Type') === 'application/json';
}

// Helper function to check if request is for page
function isPageRequest(request) {
    return request.mode === 'navigate' ||
           (request.method === 'GET' && request.headers.get('accept').includes('text/html'));
}

// Generate offline page
function getOfflinePage() {
    return new Response(`
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline - Symplifika</title>
            <style>
                body {
                    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #00FF57 0%, #00C853 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #fff;
                }
                .offline-container {
                    text-align: center;
                    background: rgba(0, 0, 0, 0.1);
                    padding: 2rem;
                    border-radius: 1rem;
                    backdrop-filter: blur(10px);
                    max-width: 400px;
                }
                .offline-icon {
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }
                h1 {
                    font-size: 1.5rem;
                    margin-bottom: 1rem;
                }
                p {
                    margin-bottom: 1.5rem;
                    opacity: 0.9;
                }
                .retry-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 0.75rem 1.5rem;
                    border-radius: 0.5rem;
                    cursor: pointer;
                    font-size: 1rem;
                    transition: all 0.2s;
                }
                .retry-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📡</div>
                <h1>Você está offline</h1>
                <p>Sem conexão com a internet. Verifique sua conexão e tente novamente.</p>
                <button class="retry-btn" onclick="window.location.reload()">
                    Tentar Novamente
                </button>
            </div>
        </body>
        </html>
    `, {
        status: 503,
        headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache'
        }
    });
}

// Handle background sync (for future implementation)
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('[SW] Background sync triggered');
        // Handle background synchronization tasks
    }
});

// Handle push notifications (for future implementation)
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    const options = {
        body: event.data ? event.data.text() : 'Nova notificação do Symplifika',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [200, 100, 200],
        tag: 'symplifika-notification',
        actions: [
            {
                action: 'open',
                title: 'Abrir',
                icon: '/static/images/action-open.png'
            },
            {
                action: 'dismiss',
                title: 'Dispensar',
                icon: '/static/images/action-dismiss.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Symplifika', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', event => {
    const { type, payload } = event.data;

    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_NAME });
            break;
        case 'CACHE_URLS':
            cacheUrls(payload.urls);
            break;
        default:
            console.log('[SW] Unknown message type:', type);
    }
});

// Cache specific URLs on demand
async function cacheUrls(urls) {
    try {
        const cache = await caches.open(DYNAMIC_CACHE_NAME);
        await cache.addAll(urls);
        console.log('[SW] URLs cached successfully');
    } catch (error) {
        console.error('[SW] Failed to cache URLs:', error);
    }
}

// Cleanup old data periodically
setInterval(() => {
    console.log('[SW] Performing periodic cleanup');

    // Clean up old cache entries (older than 7 days)
    caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        cache.keys().then(requests => {
            requests.forEach(request => {
                cache.match(request).then(response => {
                    if (response) {
                        const dateHeader = response.headers.get('date');
                        if (dateHeader) {
                            const responseDate = new Date(dateHeader);
                            const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                            if (responseDate < weekAgo) {
                                cache.delete(request);
                            }
                        }
                    }
                });
            });
        });
    });
}, 60 * 60 * 1000); // Run every hour

console.log('[SW] Service worker loaded successfully');
