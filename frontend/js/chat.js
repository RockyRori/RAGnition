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
        'referenceLink': '资料链接',
        'welcomeMessage': '你好，我是岭南大学政策问答助手，有关学校的政策问题尽管问我！',
        'errorMessage': '抱歉，我现在无法回答您的问题，请稍后再试。'
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
        'referenceLink': '資料連結',
        'welcomeMessage': '你好，我是嶺南大學政策問答助手，有關學校的政策問題儘管問我！',
        'errorMessage': '抱歉，我現在無法回答您的問題，請稍後再試。'
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
        'referenceLink': 'Reference Link',
        'welcomeMessage': 'Hello, I am the Lingnan University policy Q&A assistant, feel free to ask me any questions about school policies!',
        'errorMessage': 'Sorry, I am unable to answer your question right now, please try again later.'
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
    if(refHeaders.length > 0) {
        refHeaders.forEach(header => {
            header.textContent = translations[lang]['references'];
        });
    }
    
    const similaritySpans = document.querySelectorAll('.ref-similarity');
    if(similaritySpans.length > 0) {
        similaritySpans.forEach(span => {
            span.textContent = `${translations[lang]['similarity']}：${span.textContent.split('：')[1]}`;
        });
    }

    const referenceLink = document.querySelectorAll('.ref-link');
    if(referenceLink.length > 0) {
        referenceLink.forEach(span => {
            span.innerHTML = `<i class="fas fa-link fa-xs"></i> ${translations[lang]['referenceLink']}`;
        });
    }


}

let chats = [];
let currentChatId = null;

function createNewChat() {
    const chatId = Date.now();
    const chat = {
        id: chatId,
        title: translations[currentLang]['newChat'],
        messages: [{
            type: 'bot',
            content: translations[currentLang]['welcomeMessage']
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
            ${chat.title}
        </div>
    `).join('');
}

function switchChat(chatId) {
    currentChatId = chatId;
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

    fetch('http://localhost:8536/api/v1/feedback', {
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
                                <span class="ref-similarity">${translations[currentLang]['similarity']}：${msg.reference_simliarity[index]}</span>
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
                    ${[1,2,3,4,5].map(i => `<i class="fas fa-star ${msg.rating && i <= msg.rating ? 'active' : ''}" data-rating="${i}"></i>`).join('')}
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

    chat.messages.push({
        type: 'user',
        content: content
    });

    if (chat.isFirstMessage) {
        chat.title = content.length > 10 ? content.substring(0, 10) + '...' : content;
        chat.isFirstMessage = false;
        updateChatList();
    }

    const requestData = {
        session_id: chat.id.toString(),
        question_id: Date.now().toString(),
        previous_questions: chat.messages
           .filter(msg => msg.type === 'user')
           .map(msg => msg.content),
        current_question: content,
        language: currentLang === 'zh-CN' ? 'cn' : 
                 currentLang === 'zh-TW' ? 'tw' : 'en'
    };

    fetch('http://localhost:8536/api/v1/questions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
   .then(response => {
        if (!response.ok) {
            throw new Error(`请求失败: ${response.status} ${response.statusText}`);
        }
        return response.json();
    })
   .then(data => {
        chat.messages.push({
            type: 'bot',
            content: data.answer,
            references: data.references.map(ref => ref.content),
            reference_links: data.references.map(ref => ref.source),
            reference_simliarity: data.references.map(ref => ref.similarity),
            questionId: data.question_id,
            sessionId: data.session_id
        });
        renderMessages();
    })
   .catch(error => {
        console.error('发送消息失败:', error);
        chat.messages.push({
            type: 'bot',
            content: translations[currentLang]['errorMessage']
        });
        renderMessages();
    });

    input.value = '';
    renderMessages();
}

createNewChat();

document.getElementById('user-input').addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});