const CACHE_NAME = "ump-harvest-cache-v1";
const urlsToCache = [
  "/",
  // "/static/css/styles.css",
  // "/static/favicons/favicon-48x48.png",
  // "/static/favicons/favicon-72x72.png",
  // "/static/favicons/favicon-96x96.png",
  // "/static/favicons/favicon-144x144.png",
  // "/static/favicons/favicon-192x192.png",
  // "/static/favicons/favicon-256x256.png",
  // "/static/favicons/favicon-3  84x384.png",
  // "/static/favicons/favicon-512x512.png"
];

self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", function(event) {
  event.respondWith(
    fetch(event.request).then(function(response) {
      // If the request is successful, update the cache with the new response
      if (response.ok) {
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, response.clone());
        });
      }
      return response;
    }).catch(function() {
      // If the network request fails, fall back to the cache
      return caches.match(event.request);
    })
  );
});

self.addEventListener("activate", function(event) {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
