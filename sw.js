"use strict";
// Migration-only worker: retire earlier offline versions without caching requests.
self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{await self.clients.claim();for(const name of await caches.keys())if(name.startsWith('lab-pocket-'))await caches.delete(name);await self.registration.unregister();})()));
