// NovaGear Editorial Frontend - Client Architecture
const CHAT_API_URL = "http://127.0.0.1:8000/api/v1/chat";
const USERS_API_URL = "http://127.0.0.1:8000/api/v1/users";
const USERS_FALLBACK_URL = "http://127.0.0.1:8000/api/v1/users/users";

// Application State
let activeUser = getStoredUser();
let currentSessionId = getOrCreateSessionId();

// DOM Elements - User Modal
const userModal = document.getElementById("user-modal");
const userListContainer = document.getElementById("user-list-container");
const btnUserSwitch = document.getElementById("btn-user-switch");
const modalCloseBtn = document.getElementById("modal-close-btn");
const guestContinueBtn = document.getElementById("guest-continue-btn");
const createUserForm = document.getElementById("create-user-form");
const userDisplayName = document.getElementById("user-display-name");
const userAvatar = document.getElementById("user-avatar");

// DOM Elements - Concierge Drawer
const conciergeDrawer = document.getElementById("concierge-drawer");
const floatingLauncher = document.getElementById("floating-launcher");
const navConciergeBtn = document.getElementById("nav-concierge-btn");
const btnCloseConcierge = document.getElementById("btn-close-concierge");
const btnResetChat = document.getElementById("btn-reset-chat");
const conciergeMessages = document.getElementById("concierge-messages");
const conciergeForm = document.getElementById("concierge-form");
const conciergeInput = document.getElementById("concierge-input");
const btnSendMessage = document.getElementById("btn-send-message");
const conciergeThinking = document.getElementById("concierge-thinking");
const conciergeUserSubtext = document.getElementById("concierge-user-subtext");
const greetingParagraph = document.getElementById("greeting-paragraph");

// Initialize Application
init();

function init() {
    updateUserUI();

    // Event Listeners - Modal
    btnUserSwitch.addEventListener("click", () => openUserModal());
    modalCloseBtn.addEventListener("click", () => closeUserModal());
    guestContinueBtn.addEventListener("click", () => selectGuest());
    createUserForm.addEventListener("submit", handleCreateUser);

    // Event Listeners - Concierge Drawer
    floatingLauncher.addEventListener("click", toggleConcierge);
    navConciergeBtn.addEventListener("click", openConcierge);
    btnCloseConcierge.addEventListener("click", closeConcierge);
    btnResetChat.addEventListener("click", resetChatSession);
    conciergeForm.addEventListener("submit", handleSendMessage);

    // Open user modal on first visit if no user selected
    if (!activeUser) {
        openUserModal();
    }
}

/* --------------------------------------------------
   USER SELECTION & PROFILE MANAGEMENT
-------------------------------------------------- */

function getStoredUser() {
    try {
        const stored = localStorage.getItem("novagear_active_user");
        return stored ? JSON.parse(stored) : null;
    } catch {
        return null;
    }
}

function getOrCreateSessionId() {
    let sid = localStorage.getItem("novagear_chat_session");
    if (!sid) {
        sid = "ng_sess_" + crypto.randomUUID().slice(0, 8);
        localStorage.setItem("novagear_chat_session", sid);
    }
    return sid;
}

function updateUserUI() {
    if (activeUser) {
        userDisplayName.textContent = activeUser.name;
        userAvatar.textContent = activeUser.name.charAt(0).toUpperCase();
        conciergeUserSubtext.textContent = `Active User: ${activeUser.name} (ID: ${activeUser.id})`;
        if (greetingParagraph) {
            greetingParagraph.innerHTML = `Welcome back, <strong>${escapeHtml(activeUser.name)}</strong>. How can I assist you with NovaGear hardware or your orders today?`;
        }
    } else {
        userDisplayName.textContent = "Select Account";
        userAvatar.textContent = "?";
        conciergeUserSubtext.textContent = "Guest Session";
        if (greetingParagraph) {
            greetingParagraph.innerHTML = `Welcome to <strong>NovaGear</strong>. I am your technical concierge.`;
        }
    }
    if (window.lucide) lucide.createIcons();
}

async function openUserModal() {
    userModal.classList.remove("hidden");
    await loadUsersList();
}

function closeUserModal() {
    userModal.classList.add("hidden");
}

function selectGuest() {
    activeUser = null;
    localStorage.removeItem("novagear_active_user");
    updateUserUI();
    closeUserModal();
}

function selectUser(user) {
    activeUser = user;
    localStorage.setItem("novagear_active_user", JSON.stringify(user));
    updateUserUI();
    closeUserModal();
}

async function loadUsersList() {
    userListContainer.innerHTML = `
        <div class="text-center py-6 text-xs text-zinc-500 flex items-center justify-center gap-2">
            <span class="inline-block w-3.5 h-3.5 border-2 border-zinc-500 border-t-transparent rounded-full animate-spin"></span>
            <span>Fetching customers from database...</span>
        </div>
    `;

    try {
        // Try standard /api/v1/users first, then fallback to /api/v1/users/users
        let response = await fetch(USERS_API_URL).catch(() => null);
        if (!response || !response.ok) {
            response = await fetch(USERS_FALLBACK_URL).catch(() => null);
        }

        if (!response || !response.ok) {
            throw new Error("Unable to connect to users endpoint. Ensure FastAPI server is running.");
        }

        const users = await response.json();

        if (!users || users.length === 0) {
            userListContainer.innerHTML = `
                <div class="text-center py-6 text-xs text-zinc-400">
                    <p class="font-medium text-zinc-300">No customer profiles found</p>
                    <p class="text-[11px] text-zinc-500 mt-1">Register your first user below to test accounts.</p>
                </div>
            `;
            return;
        }

        userListContainer.innerHTML = users.map(user => {
            const isSelected = activeUser && activeUser.id === user.id;
            const initial = (user.name && user.name.charAt(0).toUpperCase()) || "U";
            return `
                <div onclick='selectUser(${JSON.stringify(user)})' class="p-3 rounded-xl border ${isSelected ? 'border-zinc-300 bg-zinc-800' : 'border-subtle bg-zinc-950/60 hover:bg-zinc-800/60'} cursor-pointer flex items-center justify-between transition group">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 rounded-full bg-zinc-800 border border-subtle flex items-center justify-center text-xs font-bold text-zinc-200">
                            ${initial}
                        </div>
                        <div>
                            <p class="text-xs font-medium text-white group-hover:text-zinc-200">${escapeHtml(user.name)}</p>
                            <p class="text-[11px] font-mono text-zinc-400">${escapeHtml(user.email)}</p>
                        </div>
                    </div>
                    <span class="text-[11px] font-mono text-zinc-500">ID: ${user.id}</span>
                </div>
            `;
        }).join("");

    } catch (err) {
        userListContainer.innerHTML = `
            <div class="p-3 rounded-xl bg-zinc-950 border border-subtle text-xs text-zinc-400 space-y-1">
                <p class="text-rose-400 font-medium">Database Unreachable</p>
                <p class="text-[11px] text-zinc-500">${escapeHtml(err.message)}</p>
                <p class="text-[11px] text-zinc-400 pt-1">Make sure backend is running: <code class="text-zinc-300">python -m uvicorn main:app</code></p>
            </div>
        `;
    }
}

async function handleCreateUser(e) {
    e.preventDefault();
    const nameInput = document.getElementById("new-user-name");
    const emailInput = document.getElementById("new-user-email");
    const btn = document.getElementById("btn-create-user");

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    if (!name || !email) return;

    btn.disabled = true;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/users/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Registration failed");
        }

        const newUser = await response.json();
        nameInput.value = "";
        emailInput.value = "";
        selectUser(newUser);
    } catch (err) {
        alert("User registration error: " + err.message);
    } finally {
        btn.disabled = false;
    }
}

/* --------------------------------------------------
   CONCIERGE DRAWER & CHAT CLIENT LOGIC
-------------------------------------------------- */

function toggleConcierge() {
    conciergeDrawer.classList.toggle("collapsed");
    floatingLauncher.classList.toggle("hidden");
    if (!conciergeDrawer.classList.contains("collapsed")) {
        conciergeInput.focus();
    }
}

function openConcierge() {
    conciergeDrawer.classList.remove("collapsed");
    floatingLauncher.classList.add("hidden");
    conciergeInput.focus();
}

function closeConcierge() {
    conciergeDrawer.classList.add("collapsed");
    floatingLauncher.classList.remove("hidden");
}

function resetChatSession() {
    currentSessionId = "ng_sess_" + crypto.randomUUID().slice(0, 8);
    localStorage.setItem("novagear_chat_session", currentSessionId);

    while (conciergeMessages.children.length > 1) {
        conciergeMessages.removeChild(conciergeMessages.lastChild);
    }

    appendSystemMessage("Conversation session reset. Memory cleared.");
}

function conciergeInquire(promptText) {
    openConcierge();
    conciergeInput.value = promptText;
    handleSendMessage(new Event("submit"));
}

async function handleSendMessage(e) {
    if (e) e.preventDefault();

    const query = conciergeInput.value.trim();
    if (!query) return;

    // 1. Render User Message Bubble
    appendUserBubble(query);
    conciergeInput.value = "";
    setLoading(true);

    try {
        // 2. Transmit to POST /api/v1/chat
        const response = await fetch(CHAT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: query,
                session_id: currentSessionId,
            }),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Server error (${response.status})`);
        }

        const data = await response.json();

        // 3. Render Assistant Response
        appendAssistantBubble(data.answer, data.sources || []);

    } catch (err) {
        console.error("Chat Error:", err);
        appendErrorBubble(err.message || "Failed to reach NovaGear AI Concierge");
    } finally {
        setLoading(false);
    }
}

function appendUserBubble(text) {
    const el = document.createElement("div");
    el.className = "flex justify-end";
    el.innerHTML = `
        <div class="chat-user-bubble p-3.5 text-xs max-w-[85%] leading-relaxed">
            ${escapeHtml(text)}
        </div>
    `;
    conciergeMessages.appendChild(el);
    scrollToBottom();
}

function appendAssistantBubble(markdown, sources) {
    const el = document.createElement("div");
    el.className = "flex items-start space-x-2.5 max-w-[95%]";

    const parsedHtml = window.marked ? marked.parse(markdown) : markdown;

    let sourcesHtml = "";
    if (sources && sources.length > 0) {
        const badges = sources.map((s, idx) => {
            const filename = (s.metadata && s.metadata.filename) || s.metadata.source || `Reference ${idx+1}`;
            const preview = escapeHtml(s.content ? s.content.slice(0, 160) + "..." : "");
            return `
                <details class="text-[10px] bg-zinc-950 border border-subtle rounded-md p-1.5 transition">
                    <summary class="cursor-pointer text-zinc-300 hover:text-white font-mono select-none flex items-center gap-1">
                        <span>📄 ${escapeHtml(filename)}</span>
                    </summary>
                    <p class="mt-1 text-zinc-400 font-mono text-[10px] bg-zinc-900 p-1.5 rounded whitespace-pre-wrap">${preview}</p>
                </details>
            `;
        }).join("");

        sourcesHtml = `
            <div class="pt-2 border-t border-subtle mt-2 space-y-1">
                <span class="text-[9px] uppercase font-mono tracking-widest text-zinc-500">Cited Knowledge (${sources.length})</span>
                <div class="space-y-1">
                    ${badges}
                </div>
            </div>
        `;
    }

    el.innerHTML = `
        <div class="w-6 h-6 rounded-md bg-zinc-800 border border-subtle flex items-center justify-center text-zinc-300 flex-shrink-0 text-xs font-mono mt-1">
            NG
        </div>
        <div class="chat-assistant-bubble p-3.5 text-xs space-y-1.5 leading-relaxed w-full">
            <div class="prose prose-invert text-xs max-w-none">
                ${parsedHtml}
            </div>
            ${sourcesHtml}
        </div>
    `;

    conciergeMessages.appendChild(el);
    if (window.lucide) lucide.createIcons();
    scrollToBottom();
}

function appendErrorBubble(errMsg) {
    const el = document.createElement("div");
    el.className = "flex items-start space-x-2.5 max-w-[95%]";
    el.innerHTML = `
        <div class="w-6 h-6 rounded-md bg-rose-950/80 border border-rose-800/80 flex items-center justify-center text-rose-300 flex-shrink-0 text-xs font-mono mt-1">
            !
        </div>
        <div class="bg-rose-950/40 border border-rose-900/60 p-3 rounded-xl text-xs text-rose-300 space-y-1 w-full">
            <p class="font-semibold text-rose-200">Concierge Offline</p>
            <p class="font-mono text-[11px] text-zinc-400">${escapeHtml(errMsg)}</p>
            <p class="text-[10px] text-zinc-500 pt-0.5">Ensure backend server is running on port 8000.</p>
        </div>
    `;
    conciergeMessages.appendChild(el);
    scrollToBottom();
}

function appendSystemMessage(msg) {
    const el = document.createElement("div");
    el.className = "text-center py-1";
    el.innerHTML = `
        <span class="text-[10px] font-mono text-zinc-500 bg-zinc-950 px-2.5 py-0.5 rounded-full border border-subtle">
            ${escapeHtml(msg)}
        </span>
    `;
    conciergeMessages.appendChild(el);
    scrollToBottom();
}

function setLoading(isLoading) {
    if (isLoading) {
        conciergeThinking.classList.remove("hidden");
        btnSendMessage.disabled = true;
        conciergeInput.disabled = true;
    } else {
        conciergeThinking.classList.add("hidden");
        btnSendMessage.disabled = false;
        conciergeInput.disabled = false;
        conciergeInput.focus();
    }
}

function scrollToBottom() {
    conciergeMessages.scrollTo({
        top: conciergeMessages.scrollHeight,
        behavior: "smooth",
    });
}

function escapeHtml(str) {
    const d = document.createElement("div");
    d.innerText = str || "";
    return d.innerHTML;
}
