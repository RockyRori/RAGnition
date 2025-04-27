// js/index.js

const translations = {
    'zh-CN': {
        'welcome': '欢迎回来，RAGnition',
        'choose': '今天我们要使用哪个知识库？',
        'home': '首页',
        'chat': '聊天',
        'file': '文件',
        'kb1': '知识库1',
        'kb2': '知识库2',
        'kb3': '知识库3',
        'docs': '文档'
    },
    'zh-TW': {
        'welcome': '歡迎回來，RAGnition',
        'choose': '今天我們要使用哪個知識庫？',
        'home': '首頁',
        'chat': '聊天',
        'file': '文件',
        'kb1': '知識庫1',
        'kb2': '知識庫2',
        'kb3': '知識庫3',
        'docs': '文檔'
    },
    'en': {
        'welcome': 'Welcome back, RAGnition',
        'choose': 'Which knowledge base to use today?',
        'home': 'Home',
        'chat': 'Chat',
        'file': 'Files',
        'kb1': 'Knowledge Base 1',
        'kb2': 'Knowledge Base 2',
        'kb3': 'Knowledge Base 3',
        'docs': 'Documents'
    }
};

let currentLang = localStorage.getItem('lang') || 'en';
updateLanguage(currentLang);
document.querySelector('#languageDropdown').textContent =
    currentLang === 'zh-CN' ? '简体中文' :
    currentLang === 'zh-TW' ? '繁體中文' : 'English';

document.querySelectorAll('[data-lang]').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const lang = this.getAttribute('data-lang');
        currentLang = lang;
        localStorage.setItem('lang', lang);
        updateLanguage(lang);
        document.querySelector('#languageDropdown').textContent =
            lang === 'zh-CN' ? '简体中文' :
            lang === 'zh-TW' ? '繁體中文' : 'English';
    });
});

function updateLanguage(lang) {
    document.querySelector('h3 strong').textContent = translations[lang]['welcome'];
    document.querySelector('h6').textContent = translations[lang]['choose'];
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === 'index.html') {
            link.textContent = translations[lang]['home'];
        } else if (link.getAttribute('href') === 'chat.html') {
            link.textContent = translations[lang]['chat'];
        } else if (link.getAttribute('href') === 'file.html') {
            link.textContent = translations[lang]['file'];
        }
    });

    document.querySelectorAll('.card h3').forEach((card, index) => {
        card.textContent = translations[lang][`kb${index + 1}`];
    });

    document.querySelectorAll('.card small').forEach(doc => {
        const count = doc.textContent.split(' ')[0];
        doc.textContent = `${count} ${translations[lang]['docs']}`;
    });
}