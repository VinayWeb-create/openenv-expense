const API_BASE = window.location.origin.includes("localhost") ? window.location.origin : "http://localhost:8002";
let totalReward = 0;
let authToken = localStorage.getItem("expense_token");
let balanceChart;
let historyData = [5000];
let labels = ["Day 0"];
let autoInterval;

// --- Auth & Session ---

async function handleAuth(type) {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msg = document.getElementById("auth-msg");

    const formData = new FormData();
    formData.append("username", user);
    formData.append("password", pass);

    try {
        const response = await fetch(`${API_BASE}/${type === 'signup' ? 'signup' : 'login'}`, {
            method: 'POST', body: formData
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Auth failed");

        if (type === 'login') {
            authToken = data.access_token;
            localStorage.setItem("expense_token", authToken);
            document.getElementById("auth-overlay").style.display = "none";
            showToast("Welcome! ✨", "emerald");
            initChart(); resetEnv();
        } else showToast("Signup Success! Login now.", "emerald");
    } catch (err) { msg.innerText = err.message; }
}

function logout() {
    localStorage.removeItem("expense_token");
    authToken = null;
    location.reload();
}

function checkToken() {
    if (authToken) {
        document.getElementById("auth-overlay").style.display = "none";
        initChart(); syncState();
    }
}

// --- Modals & Data Fetching ---

async function showHistory() {
    try {
        const res = await fetch(`${API_BASE}/history`, { headers: { "Authorization": `Bearer ${authToken}` } });
        const data = await res.json();
        let html = "<ul class='history-list'>";
        data.forEach(item => {
            html += `<li><b>Day ${item.day}:</b> ${item.action === 0 ? '🍱 Food' : (item.action === 1 ? '🏦 Save' : (item.action === 2 ? '⏳ Skip' : '🏎️ Luxury'))} | Reward: ${item.reward}</li>`;
        });
        html += "</ul>";
        openModal("Transaction History", html);
    } catch (err) { showToast("Failed to fetch history.", "rose"); }
}

async function showLeaderboard() {
    try {
        const res = await fetch(`${API_BASE}/leaderboard`);
        const data = await res.json();
        let html = "<ul class='leaderboard-list'>";
        data.forEach((l, i) => {
            html += `<li>#${i+1} <b>${l.user}</b>: $${l.balance}</li>`;
        });
        html += "</ul>";
        openModal("Global Leaderboard", html);
    } catch (err) { showToast("Failed to fetch leaderboard.", "rose"); }
}

function openModal(title, body) {
    document.getElementById("modal-overlay").style.display = "flex";
    document.getElementById("modal-title").innerText = title;
    document.getElementById("modal-body").innerHTML = body;
}

function closeModal() { document.getElementById("modal-overlay").style.display = "none"; }

// --- Advanced Actions ---

function toggleAutoPlay() {
    const isAuto = document.getElementById("auto-play-toggle").checked;
    if (isAuto) {
        autoInterval = setInterval(async () => {
            const res = await fetch(`${API_BASE}/autonomous-step`, { method: 'POST', headers: { "Authorization": `Bearer ${authToken}` } });
            const data = await res.json();
            if (data.done) { clearInterval(autoInterval); document.getElementById("auto-play-toggle").checked = false; }
            processResponse(data);
        }, 1500);
    } else clearInterval(autoInterval);
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.onstart = () => showToast("Listening... (Say Food, Save, Luxury, Skip)", "sky");
    recognition.onresult = async (event) => {
        const text = event.results[0][0].transcript;
        const res = await fetch(`${API_BASE}/voice`, { method: 'POST', headers: { "Authorization": `Bearer ${authToken}` }, body: JSON.stringify({ text }) });
        const data = await res.json();
        processResponse(data);
    };
    recognition.start();
}

// --- Chart & Environment ---

function processResponse(data) {
    totalReward += data.reward || 0;
    updateUI(data.state, data.reward, data.done);
    updateChart(data.state.day, data.state.balance);
    if (data.suggestion) document.getElementById("ai-suggestion").innerText = data.suggestion;
    if (data.done) handleGameOver(data.state);
}

async function takeAction(id) {
    const res = await fetch(`${API_BASE}/step/${id}`, { headers: { "Authorization": `Bearer ${authToken}` } });
    if (res.status === 401) return logout();
    const data = await res.json(); processResponse(data);
}

async function resetEnv() {
    const res = await fetch(`${API_BASE}/reset`, { headers: { "Authorization": `Bearer ${authToken}` } });
    const data = await res.json();
    totalReward = 0; historyData = [data.state.balance]; labels = ["Day 0"];
    if (balanceChart) { balanceChart.data.labels = labels; balanceChart.data.datasets[0].data = historyData; balanceChart.update(); }
    updateUI(data.state, 0, false); enableButtons();
}

async function syncState() {
    const res = await fetch(`${API_BASE}/state`, { headers: { "Authorization": `Bearer ${authToken}` } });
    const state = await res.json(); updateUI(state, 0, false);
}

function initChart() {
    const ctx = document.getElementById('balanceChart').getContext('2d');
    balanceChart = new Chart(ctx, {
        type: 'line', data: { labels: labels, datasets: [{ label: 'Balance', data: historyData, borderColor: '#10b981', fill: true, tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function updateChart(d, b) { labels.push(`Day ${d}`); historyData.push(b); balanceChart.update(); }

function updateUI(s, r, d) {
    document.getElementById("balance").innerText = `$${Math.round(s.balance).toLocaleString()}`;
    document.getElementById("current-day").innerText = s.day;
    document.getElementById("reward").innerText = (r || 0).toFixed(2);
    document.getElementById("total-reward").innerText = totalReward.toFixed(2);
    if (d) disableButtons();
}

function handleGameOver(s) { showToast(s.balance < 0 ? "Bankrupt!" : "Finished!", s.balance < 0 ? "rose" : "emerald"); }
function disableButtons() { document.querySelectorAll('.action-buttons button').forEach(b => b.disabled = true); }
function enableButtons() { document.querySelectorAll('.action-buttons button').forEach(b => b.disabled = false); }

function showToast(m, c) {
    const n = document.getElementById("notifications");
    const t = document.createElement("div"); t.className = "toast"; t.innerText = m; t.style.borderLeftColor = `var(--accent-${c})`;
    n.appendChild(t); setTimeout(() => { t.style.opacity = "0"; setTimeout(() => t.remove(), 500); }, 3000);
}

window.onload = checkToken;
