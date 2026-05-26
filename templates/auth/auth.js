const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginMessage.textContent = "";

  const payload = {
    username: document.getElementById("username").value.trim(),
    password: document.getElementById("password").value
  };

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (!response.ok || result.success === false) {
      loginMessage.textContent = result.message || "아이디 또는 비밀번호를 확인하세요.";
      return;
    }

    window.location.href = "/";
  } catch (error) {
    loginMessage.textContent = "서버와 통신할 수 없습니다.";
  }
});
