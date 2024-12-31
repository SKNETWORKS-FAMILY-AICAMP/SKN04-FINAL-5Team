
var uploadContent = `document.getElementById("uploadForm").addEventListener("submit", async function (e) {
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
});`;

window.uploadContent2 = function() {
    console.log('업로드 스크립트 실행됨!222');
}
