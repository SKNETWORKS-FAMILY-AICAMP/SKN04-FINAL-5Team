function loadContent22(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const mainContent = document.getElementById('main-content');
            mainContent.innerHTML = data;

            // upload4.html의 스크립트 실행
            const script = document.createElement('script');
            script.textContent = `
                document.getElementById("uploadForm").addEventListener("submit", async function (e) {
                    e.preventDefault();
                    const formData = new FormData(this);
                    document.getElementById("response").textContent = "업로드 중...";

                    try {
                       const response = await fetch("/upload", {
                           method: "POST",
                           body: formData,
                           credentials: 'include'
                       });

                       const result = await response.json();
                       const message = response.ok ? result.message : result.detail || result.error;
                       document.getElementById("response").innerText = message;
                    } catch (error) {
                       document.getElementById("response").innerText = "파일 업로드 중 오류가 발생했습니다.";
                    }
                });
            `;
            mainContent.appendChild(script);


            // 상단바와 사이드바 유지를 위한 처리
            const topbar = document.querySelector('.navbar.topbar');
            const sidebar = document.querySelector('.sidebar');
            
            // 상단바와 사이드바가 존재하면 유지
            if (topbar) topbar.classList.remove('d-none');
            if (sidebar) sidebar.classList.remove('d-none');

            const sendButton = document.getElementById('sendButton');
            const userInput = document.getElementById('userInput');                

            if (sendButton && userInput) {                
                sendButton.addEventListener('click', handleSendMessage);
                
                // Enter 키로도 메시지 전송 가능
                userInput.addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        handleSendMessage();
                    }
                });
            }

        })
        .catch(error => {
            console.error('Error loading content:', error);
            alert("컨텐츠를 불러오는데 실패했습니다");
        });
}