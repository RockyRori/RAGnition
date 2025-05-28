// js/index.js

const translations = {
    'zh-CN': {
        'welcome': '欢迎回来，岭南的朋友',
        'choose': '今天我们要用哪个知识库？',
        'home': '首页',
        'chat': '聊天',
        'file': '文件',
        'kb1': '岭南大学政策文件',
        'kb2': '数据科学学院知识库',
        'docs': '文档'
    },
    'zh-TW': {
        'welcome': '歡迎返嚟，嶺南嘅老友',
        'choose': '今日我哋揀邊個知識庫？',
        'home': '首頁',
        'chat': '聊天',
        'file': '文件',
        'kb1': '嶺南大學政策文件',
        'kb2': '數據科學學院知識庫',
        'docs': '文檔'
    },
    'en': {
        'welcome': 'Welcome back, Lingnan folks',
        'choose': 'Which knowledge base to use today?',
        'home': 'Home',
        'chat': 'Chat',
        'file': 'Files',
        'kb1': 'Lingnan University Policy Documents',
        'kb2': 'School of Data Science Base',
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
document.addEventListener('DOMContentLoaded', function() {
    const lingnan = document.getElementById('lingnan');
    const base_DS = document.getElementById('base_DS');

    // 只有当没有存储过激活卡片时，才设置默认值
    const activeCardId = localStorage.getItem('activeCard');
    if (!activeCardId) {
        lingnan.classList.add('active');
        localStorage.setItem('activeCard', 'lingnan');
    }else {
        // 如果已有存储记录，则恢复上次选择
        [lingnan, base_DS].forEach(c => c.classList.remove('active'));
        const previouslyActive = document.getElementById(activeCardId);
        if (previouslyActive) previouslyActive.classList.add('active');
    }

    [lingnan, base_DS].forEach(card => {
        card.addEventListener('click', function() {
            [lingnan, base_DS].forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            localStorage.setItem('activeCard', this.id);
        });
    });
});