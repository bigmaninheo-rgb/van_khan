const CACHE_NAME = 'van-khan-v2';
const urlsToCache = [
    '/',
    '/index.html',
    '/index_enhanced.html',
    '/prayers.html',
    '/manifest.json',
    '/icons/icon-192.png',
    '/icons/icon-512.png',
    '/icons/apple-touch-icon-192.png',
    '/icons/icon-maskable-192.png',
    '/icons/icon-maskable-512.png',
    // Cache all prayer pages for offline access
    '/prayer1.html', '/prayer2.html', '/prayer3.html', '/prayer4.html', '/prayer5.html',
    '/prayer6.html', '/prayer7.html', '/prayer8.html', '/prayer9.html', '/prayer10.html',
    '/prayer11.html', '/prayer12.html', '/prayer13.html', '/prayer14.html', '/prayer15.html',
    '/prayer16.html', '/prayer17.html', '/prayer18.html', '/prayer19.html', '/prayer20.html',
    '/prayer21.html', '/prayer22.html', '/prayer23.html', '/prayer24.html', '/prayer25.html',
    '/prayer26.html', '/prayer27.html', '/prayer28.html', '/prayer29.html', '/prayer30.html',
    '/prayer31.html', '/prayer32.html', '/prayer33.html', '/prayer34.html', '/prayer35.html',
    '/prayer36.html', '/prayer37.html', '/prayer38.html', '/prayer39.html', '/prayer40.html',
    '/prayer41.html', '/prayer42.html', '/prayer43.html', '/prayer44.html', '/prayer45.html',
    '/prayer46.html'
];

// Install event - cache all resources
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching all resources');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.error('Service Worker: Failed to cache resources:', error);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit - return response
                if (response) {
                    console.log('Service Worker: Serving from cache:', event.request.url);
                    return response;
                }

                // Not in cache - fetch from network
                return fetch(event.request)
                    .then((response) => {
                        // Check if valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone response for caching
                        const responseToCache = response.clone();
                        
                        // Cache new resources
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // Network failed - try to serve from cache
                        console.log('Service Worker: Network failed, serving from cache');
                        return caches.match(event.request);
                    });
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for notifications
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Handle background sync tasks
            console.log('Service Worker: Background sync triggered')
        );
    }
});

// Push notification handler
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'Có bài văn khấn mới hoặc nhắc nhở ngày lễ!',
        icon: '/icons/icon-192.png',
        badge: '/icons/icon-192.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Xem ngay',
                icon: '/icons/icon-192.png'
            },
            {
                action: 'close',
                title: 'Đóng',
                icon: '/icons/icon-192.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Văn Khấn', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
