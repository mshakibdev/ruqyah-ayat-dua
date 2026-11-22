/* রুকইয়াহ — আয়াত ও দোয়া · সার্ভিস ওয়ার্কার
   নথি বদলালে VERSION বাড়িয়ে দিন (v1 → v2), নইলে পুরনো ক্যাশ থেকেই দেখাবে */
const VERSION = 'ruqyah-ayat-dua-v3';

const ASSETS = [
  './',
  './index.html',
  './tair.html',
  './dua.html',
  './kobor-ayat.html',
  './kobor-dua.html',
  './style.css',
  './app.js',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './icons/apple-touch-icon.png',
  './fonts/noto-sans-bengali-bengali-400-normal.woff2',
  './fonts/noto-sans-bengali-bengali-600-normal.woff2',
  './fonts/noto-sans-bengali-bengali-700-normal.woff2',
  './fonts/noto-serif-bengali-bengali-600-normal.woff2',
  './fonts/noto-naskh-arabic-arabic-400-normal.woff2'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) =>
      // একটি ফাইল না পেলেও যেন পুরো ইনস্টল আটকে না যায়
      Promise.all(ASSETS.map((u) =>
        c.add(new Request(u, { cache: 'reload' })).catch(() => {})
      ))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== self.location.origin) return;

  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res && res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => {
        // অফলাইনে অচেনা পাতায় গেলে হোমে ফেরত
        if (req.mode === 'navigate') return caches.match('./index.html');
        return Response.error();
      });
    })
  );
});
