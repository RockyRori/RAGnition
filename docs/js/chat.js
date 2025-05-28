// js/chat.js

const translations = {
    'zh-CN': {
        'home': '首页',
        'chat': '聊天',
        'file': '文件',
        'newChat': '新建对话',
        'inputPlaceholder': '请输入您的问题（最多2000字）...',
        'send': '发送',
        'references': '参考资料',
        'similarity': '相似度',
        'referenceLink': '资料链接'
    },
    'zh-TW': {
        'home': '首頁',
        'chat': '聊天',
        'file': '文件',
        'newChat': '新建對話',
        'inputPlaceholder': '請輸入您的問題（最多2000字）...',
        'send': '發送',
        'references': '參考資料',
        'similarity': '相似度',
        'referenceLink': '資料連結'
    },
    'en': {
        'home': 'Home',
        'chat': 'Chat',
        'file': 'Files',
        'newChat': 'New Chat',
        'inputPlaceholder': 'Enter your question here (max 2000 chars)...',
        'send': 'Send',
        'references': 'References',
        'similarity': 'Similarity',
        'referenceLink': 'Reference Link'
    }
};

const botMessages = {
    lingnan: {
        'zh-CN': '你好，我是岭南大学政策问答助手，有关学校的政策问题尽管问我！',
        'zh-TW': '你好，我係嶺南大學政策答問小幫手，有關學校嘅政策問題，隨便問！',
        'en': 'Hello, I am the Lingnan University policy QA assistant, feel free to ask me any questions about school policies!'
    },
    base_DS: {
        'zh-CN': '欢迎数据科学学院的同学们，有关数据科学的政策问题尽管问我！',
        'zh-TW': '歡迎數據科學學院嘅同學仔！有關數據科學嘅政策問題，隨便問我啦！',
        'en': 'Welcome back my DS fellows, feel free to ask me any questions about DS policies!'
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
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === 'index.html') {
            link.textContent = translations[lang]['home'];
        } else if (link.getAttribute('href') === 'chat.html') {
            link.textContent = translations[lang]['chat'];
        } else if (link.getAttribute('href') === 'file.html') {
            link.textContent = translations[lang]['file'];
        }
    });

    document.querySelector('.new-chat-btn').innerHTML = `<i class="fas fa-plus"></i> ${translations[lang]['newChat']}`;
    document.getElementById('user-input').placeholder = translations[lang]['inputPlaceholder'];
    document.querySelector('.send-btn').innerHTML = `<i class="fas fa-paper-plane"></i> ${translations[lang]['send']}`;

    const refHeaders = document.querySelectorAll('.reference-content h6');
    if (refHeaders.length > 0) {
        refHeaders.forEach(header => {
            header.textContent = translations[lang]['references'];
        });
    }

    const similaritySpans = document.querySelectorAll('.ref-similarity');
    if (similaritySpans.length > 0) {
        similaritySpans.forEach(span => {
            span.textContent = `${translations[lang]['similarity']}：${span.textContent.split('：')[1]}`;
        });
    }

    const referenceLink = document.querySelectorAll('.ref-link');
    if (referenceLink.length > 0) {
        referenceLink.forEach(span => {
            span.innerHTML = `<i class="fas fa-link fa-xs"></i> ${translations[lang]['referenceLink']}`;
        });
    }


}
//TODO：记录历史会话
//// —— 在脚本最前面 ——
//// 1) 从 localStorage 读取
//let chats = JSON.parse(localStorage.getItem('chats') || '[]');
//// 2) 恢复上次打开的会话（可选：这里我们默认第一条）
//let currentChatId = chats.length ? chats[0].id : null;
//
//// 页面加载后渲染列表和消息
//window.onload = () => {
//    updateChatList();
//    if (currentChatId !== null) renderMessages();
//};
//
// 保存到 localStorage 的小函数


let chats = [];
let currentChatId = null;

function createNewChat() {
    const base = localStorage.getItem('activeCard') || 'lingnan';
    const welcome = (botMessages[base] && botMessages[base][currentLang]) || botMessages['lingnan'][currentLang];

    const chatId = Date.now();
    const chat = {
        id: chatId,
        title: translations[currentLang]['newChat'],
        messages: [{
            type: 'bot',
            content: welcome
        }],
        isFirstMessage: true
    };
    chats.push(chat);
    currentChatId = chatId;
    updateChatList();
    renderMessages();
}

function updateChatList() {
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item ${chat.id === currentChatId ? 'active' : ''}" 
             onclick="switchChat(${chat.id})">
            <i class="fas fa-comment"></i>
            <span class="chat-title">${chat.title}</span>
            <!-- 删除按钮 -->
            <span class="delete-icon" style="float: right; cursor: pointer; padding: 0 5px; color: red;" onclick="deleteChat(${chat.id}); event.stopPropagation();">
                <i class="fas fa-trash"></i>
            </span>
        </div>
    `).join('');
}

function saveChats() {
    localStorage.setItem('chats', JSON.stringify(chats));
}

function switchChat(chatId) {
    currentChatId = chatId;
    updateChatList();
    renderMessages();
}

function deleteChat(chatId) {
    chats = chats.filter(c => c.id !== chatId);
    if (currentChatId === chatId) {
        currentChatId = chats.length ? chats[0].id : null;
    }
    saveChats();
    updateChatList();
    renderMessages();
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('fa-star')) {
        handleStarClick(event);
    }
});

function handleStarClick(event) {
    const star = event.target;
    if (!star.classList.contains('fa-star')) return;

    const rating = parseInt(star.dataset.rating);
    const container = star.parentElement;

    container.querySelectorAll('i').forEach((s, index) => {
        s.classList.toggle('active', index < rating);
    });

    container.dataset.rated = rating;

    const chat = chats.find(c => c.id === currentChatId);
    if (!chat) return;

    const lastBotMessage = chat.messages.findLast(msg => msg.type === 'bot');
    if (!lastBotMessage) return;

    lastBotMessage.rating = rating;

    const sessionId = lastBotMessage.sessionId;
    const questionId = lastBotMessage.questionId;

    const feedbackData = {
        session_id: sessionId,
        question_id: questionId,
        rating: rating * 2
    };

    fetch(URLS.FEEDBACK, {
            method: 'GET',
            body: JSON.stringify(feedbackData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`反馈提交失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        });
}

function renderMessages() {
    const chat = chats.find(c => c.id === currentChatId);
    if (!chat) return;

    const container = document.getElementById('chat-container');
    container.innerHTML = chat.messages.map(msg => `
        <div class="message ${msg.type === 'user' ? 'user-message' : ''}">
            <img src="static/${msg.type === 'user' ? 'users.png' : 'bot.png'}" class="avatar">
            <div class="message-content">
                ${msg.content}
            </div>
        </div>
        ${msg.references ? `
            <div class="reference-container">
                <div class="reference-content">
                    <h6>${translations[currentLang]['references']}</h6>
                    ${msg.references.map((ref, index) => `
                        <div class="reference-item">
                            <div class="ref-header">
                                <span class="ref-number">[${index + 1}]</span>
                                <span class="ref-content">${ref}</span>
                                <button class="expand-btn" onclick="toggleExpand(this)">
                                    <i class="fas fa-chevron-down"></i>
                                </button>
                            </div>
                            <div class="ref-meta">
                                ${msg.reference_links && msg.reference_links[index] ?
            `<a href="${msg.reference_links[index]}" class="ref-link"><i class="fas fa-link fa-xs"></i> ${translations[currentLang]['referenceLink']}</a>` :
            ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ${msg.type === 'bot' ? `
            <div class="rating-container">
                <div class="star-rating" ${msg.rating ? `data-rated="${msg.rating}"` : ''}>
                    ${[1, 2, 3, 4, 5].map(i => `<i class="fas fa-star ${msg.rating && i <= msg.rating ? 'active' : ''}" data-rating="${i}"></i>`).join('')}
                </div>
            </div>
            ` : ''}
        ` : ''}
    `).join('');
    container.scrollTop = container.scrollHeight;
}

function toggleExpand(button) {
    const content = button.previousElementSibling;
    const isExpanded = content.classList.contains('expanded');

    content.classList.toggle('expanded');
    button.classList.toggle('expanded');
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const content = input.value.trim();
    if (!content) return;

    const chat = chats.find(c => c.id === currentChatId);
    if (!chat) return;

    // add user message
    chat.messages.push({
        type: 'user',
        content
    });
    if (chat.isFirstMessage) {
        chat.title = content.length > 10 ? content.slice(0, 10) + '...' : content;
        chat.isFirstMessage = false;
        updateChatList();
    }

    // prepare bot placeholder
    const botMessage = {
        type: 'bot',
        content: ''
    };
    chat.messages.push(botMessage);
    renderMessages();

    // build SSE URL
    const requestData = {
        session_id: chat.id.toString(),
        question_id: Date.now().toString(),
        previous_questions: chat.messages.filter(m => m.type === 'user').map(m => m.content),
        current_question: content,
        language: currentLang === 'zh-CN' ? 'zh-cn' : (currentLang === 'zh-TW' ? 'zh-tw' : 'en'),
        base: localStorage.getItem('activeCard') || 'lingnan'
    };
    const url = new URL(URLS.STREAM);
    Object.entries(requestData).forEach(([k, v]) => {
        url.searchParams.append(k, typeof v === 'string' ? v : JSON.stringify(v));
    });

    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
        if (event.data === "[DONE]") {
            eventSource.close();
            return;
        }
        const data = JSON.parse(event.data);
        if (data.references) {
            botMessage.references = data.references.map(r => r.content);
            botMessage.reference_links = data.references.map(r => r.source);
            botMessage.reference_simliarity = data.references.map(r => r.similarity);
        } else if (data.token) {
            botMessage.content += data.token;
        }
        renderMessages();
    };
    eventSource.onerror = () => {
        eventSource.close();
        botMessage.content += " [连接中断]";
        renderMessages();
    };

    input.value = '';
}

createNewChat();

document.getElementById('user-input').addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});