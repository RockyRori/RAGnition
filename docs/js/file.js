// js/file.js

const translations = {
    'zh-CN': {
        'welcome': '欢迎回来，岭南的朋友',
        'choose': '今天我们要使用哪个知识库？',
        'home': '首页',
        'chat': '聊天',
        'file': '文件',
        'docs': '文档',
        'file_name': '文件名称',
        'file_description': '文件描述',
        'upload_date': '上传日期',
        'file_size': '文件大小',
        'operation': '操作',
        'upload_file': '上传文件',
        'upload_title': '上传文件',
        'upload_hint': '将文件拖放到此处，或点击选择文件',
        'submit': '提交',
        'preview': '预览'
    },
    'zh-TW': {
        'welcome': '歡迎返嚟，嶺南嘅老友',
        'choose': '今天我們要使用哪個知識庫？',
        'home': '首頁',
        'chat': '聊天',
        'file': '文件',
        'docs': '文檔',
        'file_name': '文件名稱',
        'file_description': '文件描述',
        'upload_date': '上傳日期',
        'file_size': '文件大小',
        'operation': '操作',
        'upload_file': '上傳文件',
        'upload_title': '上傳文件',
        'upload_hint': '將文件拖放到此處，或點擊選擇文件',
        'submit': '提交',
        'preview': '預覽'
    },
    'en': {
        'welcome': 'Welcome back, Lingnan folks',
        'choose': 'Which knowledge base to use today?',
        'home': 'Home',
        'chat': 'Chat',
        'file': 'Files',
        'docs': 'Documents',
        'file_name': 'File Name',
        'file_description': 'Description',
        'upload_date': 'Upload Date',
        'file_size': 'File Size',
        'operation': 'Action',
        'upload_file': 'Upload File',
        'upload_title': 'Upload File',
        'upload_hint': 'Drag and drop files here, or click to select',
        'submit': 'Submit',
        'preview': 'preview'
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

document.addEventListener('DOMContentLoaded', function() {
    const activeCard = localStorage.getItem('activeCard');
    // if (activeCard) {
    //     alert(`当前激活的卡片是: ${activeCard}`);
    // }
});

function updateLanguage(lang) {
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === 'index.html') {
            link.textContent = translations[lang]['home'];
        } else if (link.getAttribute('href') === 'chat.html') {
            link.textContent = translations[lang]['chat'];
        } else if (link.getAttribute('href') === 'file.html') {
            link.textContent = translations[lang]['file'];
        }
    });

    // Update table headers
    const ths = document.querySelectorAll('.table thead th');
    if (ths.length >= 5) {
        ths[0].textContent = translations[lang]['file_name'];
        ths[1].textContent = translations[lang]['file_description'];
        ths[2].textContent = translations[lang]['upload_date'];
        ths[3].textContent = translations[lang]['file_size'];
        ths[4].textContent = translations[lang]['operation'];
    }

    document.querySelectorAll('.badge.bg-secondary').forEach(badge => {
        badge.textContent = translations[lang]['preview'];
    });

    // Update upload button and modal elements
    const uploadBtn = document.querySelector('.upload-btn');
    if (uploadBtn) {
        uploadBtn.innerHTML = `<i class="fas fa-upload"></i> ${translations[lang]['upload_file']}`;
    }

    const uploadTitle = document.querySelector('#uploadModal h3');
    if (uploadTitle) {
        uploadTitle.textContent = translations[lang]['upload_title'];
    }

    const uploadHint = document.querySelector('#dropZone p');
    if (uploadHint) {
        uploadHint.textContent = translations[lang]['upload_hint'];
    }

    const submitBtn = document.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.textContent = translations[lang]['submit'];
    }
}