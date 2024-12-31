function handleSendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (message.length === 0) return;

    // 사용자 메시지 표시
    displayMessage(message, 'user');
    
    // 타이핑 인디케이터 표시
    document.getElementById('typingIndicator').style.display = 'flex';
    
    // 입력 필드 비우기
    userInput.value = '';
    userInput.disabled = true;

    // ChatGPT API 호출
    fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 타이핑 인디케이터 숨기기
        document.getElementById('typingIndicator').style.display = 'none';
        
        // 봇 메시지 표시
        displayMessage(data.reply, 'bot');
        
        // 입력 필드 다시 활성화
        userInput.disabled = false;
        userInput.focus();
    })
    .catch(error => {
        console.error('Error:', error);
        
        // 타이핑 인디케이터 숨기기
        document.getElementById('typingIndicator').style.display = 'none';
        
        // 입력 필드 다시 활성화
        userInput.disabled = false;
        
        // 오류 메시지 표시
        displayMessage('서버 응답에 문제가 있습니다. 다시 시도해주세요.', 'bot');
    });
}

function displayMessage(message, sender) {
    // const messagesDiv = document.getElementById('messages');
    // const messageDiv = document.createElement('div');
    // messageDiv.className = `message ${sender}-message`;
    // messageDiv.textContent = message;
    
    // // 타이핑 인디케이터 앞에 메시지 추가
    // const typingIndicator = document.getElementById('typingIndicator');
    // messagesDiv.insertBefore(messageDiv, typingIndicator);
    
    // // 스크롤을 가장 아래로
    // messagesDiv.scrollTop = messagesDiv.scrollHeight;

    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `message-avatar ${sender}-avatar`;
    avatarDiv.textContent = sender === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // 타이핑 인디케이터 앞에 메시지 추가
    const typingIndicator = document.getElementById('typingIndicator');
    messagesDiv.insertBefore(messageDiv, typingIndicator);
    
    // 스크롤을 가장 아래로
    messagesDiv.scrollTop = messagesDiv.scrollHeight;    
}
