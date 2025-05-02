// js/url.js

// 本地开发时设为 true，部署到服务器时设为 false
const USE_LOCAL = true;

const LOCAL_BASE = 'http://localhost:8536/api/v1';
const SERVER_BASE = 'https://ipaq-brass-patch-travis.trycloudflare.com/api/v1';

// 根据开关选取基础 URL
const BASE = USE_LOCAL ? LOCAL_BASE : SERVER_BASE;

window.URLS = {
    BASE,
    FEEDBACK: `${BASE}/feedback`,
    QUESTIONS: `${BASE}/questions`,
    STREAM: `${BASE}/questions/stream`,
    FILE_UPLOAD: `${BASE}/files`,
    FILES_LIST: `${BASE}/files/list`,
    FILE_PREVIEW: `${BASE}/files/preview`,
};