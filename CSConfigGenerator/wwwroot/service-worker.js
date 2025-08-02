// In development, always fetch from the network and do not enable offline support.
// This is because caching would make development more difficult (changes would not
// be reflected on the first load after each change).
self.importScripts('./service-worker-assets.js');

const cacheName = `offline-cache-${self.assetsManifest.version}`;

self.addEventListener('install', async event => {
    console.log('Installing service worker...');
    const cache = await caches.open(cacheName);
    await cache.addAll(self.assetsManifest.assets.map(asset => asset.url));
    // Activate the new service worker as soon as the old one is gone.
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Activating service worker...');
    // Delete old caches
    event.waitUntil(
        caches.keys().then(async (cacheNames) => {
            await Promise.all(
                cacheNames.map(name => {
                    if (name.startsWith('offline-cache-') && name !== cacheName) {
                        return caches.delete(name);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    const isGet = event.request.method === 'GET';
    const isHttp = event.request.url.startsWith('http');
    if (isGet && isHttp) {
        event.respondWith(
            (async () => {
                const cache = await caches.open(cacheName);
                const cachedResponse = await cache.match(event.request);
                if (cachedResponse) {
                    return cachedResponse;
                }

                const networkResponse = await fetch(event.request);
                // Do not cache responses that are not ok
                if (networkResponse.ok) {
                    // Do not cache opaque responses
                    if(networkResponse.type !== 'opaque') {
                        await cache.put(event.request, networkResponse.clone());
                    }
                }
                return networkResponse;
            })()
        );
    }
});
