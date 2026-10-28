// 讓網頁可以安裝到主畫面；不做快取，菜單更新會立即生效
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
