self.addEventListener("install", event => {
  console.log("Rafiq PWA Installed");
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  console.log("Rafiq PWA Activated");
});

self.addEventListener("fetch", event => {
  event.respondWith(fetch(event.request));
});
