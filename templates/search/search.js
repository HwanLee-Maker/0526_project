const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const contactForm = document.getElementById("contactForm");
const logoutButton = document.getElementById("logoutButton");
const tableBody = document.getElementById("contactTableBody");
const resultCount = document.getElementById("resultCount");
const contactMessage = document.getElementById("contactMessage");
let searchTimer = null;

const FIELD_RULES = {
  name: {
    label: "이름",
    maxLength: 40,
    pattern: /^[가-힣a-zA-Z0-9\s._-]+$/
  },
  phone: {
    label: "전화번호",
    maxLength: 20,
    pattern: /^[0-9+\-\s()]+$/
  },
  address: {
    label: "집주소",
    maxLength: 120,
    pattern: /^[가-힣a-zA-Z0-9\s.,()#/_-]+$/
  }
};

function cleanField(value) {
  return String(value ?? "")
    .replace(/[\u0000-\u001f\u007f]/g, "")
    .trim();
}

function validateField(key, value) {
  const rule = FIELD_RULES[key];

  if (!value) {
    return `${rule.label}을 입력하세요.`;
  }

  if (value.length > rule.maxLength) {
    return `${rule.label}은 ${rule.maxLength}자 이하로 입력하세요.`;
  }

  if (!rule.pattern.test(value)) {
    return `${rule.label}에 사용할 수 없는 문자가 있습니다.`;
  }

  return "";
}

function makeCell(value) {
  const cell = document.createElement("td");
  cell.textContent = String(value ?? "");
  return cell;
}

function normalizeContacts(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.contacts)) return data.contacts;
  return [];
}

function renderContacts(contacts) {
  resultCount.textContent = `${contacts.length}건`;

  if (contacts.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="3" class="empty-cell">검색 결과가 없습니다.</td></tr>';
    return;
  }

  tableBody.replaceChildren(...contacts.map((contact) => {
    const row = document.createElement("tr");
    row.append(
      makeCell(contact.name),
      makeCell(contact.phone),
      makeCell(contact.address)
    );
    return row;
  }));
}

async function loadContacts(query = "") {
  const url = query ? `/api/contacts?q=${encodeURIComponent(query)}` : "/api/contacts";
  const response = await fetch(url, { headers: { "Accept": "application/json" } });

  if (response.status === 401) {
    window.location.href = "/login";
    return;
  }

  if (!response.ok) {
    tableBody.innerHTML = '<tr><td colspan="3" class="empty-cell">주소록을 불러오지 못했습니다.</td></tr>';
    resultCount.textContent = "0건";
    return;
  }

  const data = await response.json();
  renderContacts(normalizeContacts(data));
}

function requestSearch() {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => {
    loadContacts(searchInput.value.trim());
  }, 180);
}

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadContacts(searchInput.value.trim());
});

searchInput.addEventListener("input", requestSearch);

contactForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  contactMessage.textContent = "";

  const payload = {
    name: cleanField(document.getElementById("name").value),
    phone: cleanField(document.getElementById("phone").value),
    address: cleanField(document.getElementById("address").value)
  };

  for (const key of Object.keys(FIELD_RULES)) {
    const message = validateField(key, payload[key]);
    if (message) {
      contactMessage.textContent = message;
      document.getElementById(key).focus();
      return;
    }
  }

  try {
    const response = await fetch("/api/contacts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (!response.ok || result.success === false) {
      contactMessage.textContent = result.message || "연락처 추가에 실패했습니다.";
      return;
    }

    contactForm.reset();
    searchInput.value = "";
    window.clearTimeout(searchTimer);
    contactMessage.textContent = "연락처가 추가되었습니다.";
    await loadContacts();
  } catch (error) {
    contactMessage.textContent = "서버와 통신할 수 없습니다.";
  }
});

logoutButton.addEventListener("click", async () => {
  await fetch("/api/logout", { method: "POST" });
  window.location.href = "/login";
});

loadContacts();
