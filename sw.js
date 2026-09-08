"use strict";
/* Service worker du Lecteur rétro : cache offline (stale-while-revalidate).
   Utile uniquement quand la page est SERVIE (http/https) ; en file:// il n'est pas utilisé. */
const CACHE = 'lecteur-retro-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => {
  try { const ks = await caches.keys(); await Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))); } catch (e) {}
  await self.clients.claim();
})()));
self.addEventListener('fetch', event => {
  const req = event.request; if (req.method !== 'GET') return;
  let url; try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;
  if (url.protocol !== 'https:' && url.protocol !== 'http:') return;
  event.respondWith((async () => {
    try {
      const cache = await caches.open(CACHE);
      if (req.mode === 'navigate') {
        try { const net = await fetch(req); if (net && net.ok && net.type === 'basic') await cache.put(req, net.clone()); return net; }
        catch (e) { const c = await cache.match(req); if (c) return c; throw e; }
      }
      const hit = await cache.match(req);
      if (hit) {
        event.waitUntil((async () => { try { const f = await fetch(req); if (f && f.ok && f.type === 'basic') await cache.put(req, f.clone()); } catch (e) {} })());
        return hit;
      }
      const r = await fetch(req);
      try { if (r && r.ok && r.status === 200 && r.type === 'basic') await cache.put(req, r.clone()); } catch (e) {}
      return r;
    } catch (e) { return fetch(req); }
  })());
});
