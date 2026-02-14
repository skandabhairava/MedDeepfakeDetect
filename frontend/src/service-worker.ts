const CACHE_NAME = 'medical-analyzer-v1';
const STATIC_CACHE = 'medical-analyzer-static-v1';

// Only cache static assets, not dynamic SvelteKit chunks
const urlsToCache = [
  '/',
  '/index.html',
  '/favicon.ico',
  '/favicon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/manifest.webmanifest',
];

// Install event - cache static resources only
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Opened static cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Fetch event - only cache static assets, let dynamic content pass through
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Don't cache SvelteKit dynamic content
  if (url.pathname.startsWith('/_app/') || 
      url.pathname.startsWith('/@/') ||
      request.headers.get('X-Requested-With') === 'XMLHttpRequest' ||
      request.mode === 'cors') {
    // Let dynamic requests pass through without caching
    return;
  }
  
  // Only handle GET requests for static assets
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle HTML files - always try network first, fallback to cache
  if (url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request) || caches.match('/index.html');
        })
    );
    return;
  }
  
  // Cache static assets only
  event.respondWith(
    caches.match(request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request
        const fetchRequest = request.clone();

        return fetch(fetchRequest).then(
          (response) => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Only cache static files (images, css, js that aren't SvelteKit chunks)
            const isStaticAsset = url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot|json|webp)$/);
            
            if (isStaticAsset && !url.pathname.includes('/_app/')) {
              // Clone the response
              const responseToCache = response.clone();

              caches.open(STATIC_CACHE)
                .then((cache) => {
                  cache.put(request, responseToCache);
                });
            }

            return response;
          }
        ).catch(() => {
          // Return cached version if available for static assets
          return caches.match(request);
        });
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== CACHE_NAME) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all pages
      self.clients.claim()
    ])
  );
});

// Background sync for when connection is restored
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from Medical Analyzer',
    icon: '/icon-192.png',
    badge: '/favicon.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('Medical Analyzer', options)
  );
});

function doBackgroundSync() {
  // Handle any pending requests that failed while offline
  console.log('Background sync completed');
}
