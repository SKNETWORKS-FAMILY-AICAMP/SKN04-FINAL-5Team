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
        body: JSON.stringify({ 
            username: 'user',  // 여기에 실제 사용자 이름을 입력
            password: '1111',  // 여기에 실제 비밀번호를 입력
            message: message 
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {

        console.log("data.output.result.content:" , data.output.result.content )            

        // API 응답 처리
        const botReply = ( data.output?.result.content || '응답을 처리할 수 없습니다.' )
            .replace(/\n/g, '<br>')  // \n을 <br>로 변환
            .replace(/<br><br>/g, '<br>');  // 연속된 <br>를 하나로 줄이기   
            
        console.log("botReply:" , botReply)            
        
        // 타이핑 인디케이터 숨기기
        document.getElementById('typingIndicator').style.display = 'none';
        
        // 봇 메시지 표시
        displayMessage(botReply, 'bot');
        
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

    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `message-avatar ${sender}-avatar`;
    avatarDiv.textContent = sender === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = message;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // 타이핑 인디케이터 앞에 메시지 추가
    const typingIndicator = document.getElementById('typingIndicator');
    messagesDiv.insertBefore(messageDiv, typingIndicator);
    
    // 스크롤을 가장 아래로
    messagesDiv.scrollTop = messagesDiv.scrollHeight;    
}
