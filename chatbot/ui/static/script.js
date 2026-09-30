// State variables
let currentThreadId = null;
let isProcessing = false;
let messageHistory = []; // stores messages and their retrieved chunks

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const togglePanelBtn = document.getElementById("togglePanelBtn");
const closePanelBtn = document.getElementById("closePanelBtn");
const chunksPanel = document.getElementById("chunksPanel");
const chunksList = document.getElementById("chunksList");
const ragQueryDisplay = document.getElementById("ragQueryDisplay");
const chunksCountBadge = document.getElementById("chunksCountBadge");
const threadDisplay = document.getElementById("threadDisplay");
const welcomeCard = document.getElementById("welcomeCard");

// Configure Marked options
if (typeof marked !== "undefined") {
    marked.setOptions({
        breaks: true,
        highlight: function (code, lang) {
            if (typeof hljs !== "undefined" && lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return typeof hljs !== "undefined" ? hljs.highlightAuto(code).value : code;
        }
    });
}

// Generate unique thread ID on startup
function initThread() {
    currentThreadId = "thread-" + Math.random().toString(36).substring(2, 10) + "-" + Date.now().toString(36);
    threadDisplay.textContent = "Session: " + currentThreadId.substring(0, 15) + "...";
}

// Helper: Auto-expand textarea
userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 140) + "px";
});

// Handle keydown: Enter to send, Shift+Enter for newline
userInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

sendBtn.addEventListener("click", handleSendMessage);

newChatBtn.addEventListener("click", () => {
    if (isProcessing) return;
    initThread();
    chatMessages.innerHTML = "";
    if (welcomeCard) {
        chatMessages.appendChild(welcomeCard);
    }
    clearChunksPanel();
});

togglePanelBtn.addEventListener("click", () => {
    chunksPanel.classList.toggle("collapsed");
});

closePanelBtn.addEventListener("click", () => {
    chunksPanel.classList.add("collapsed");
});

const ingestBtn = document.getElementById("ingestBtn");
if (ingestBtn) {
    ingestBtn.addEventListener("click", async () => {
        const origHtml = ingestBtn.innerHTML;
        ingestBtn.disabled = true;
        ingestBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Ingesting...';
        try {
            const res = await fetch("/api/ingest", { method: "POST" });
            const data = await res.json();
            alert(data.message || data.error || "Done");
        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            ingestBtn.disabled = false;
            ingestBtn.innerHTML = origHtml;
        }
    });
}

// Prompt suggestion chip handler
function sendPrompt(text) {
    userInput.value = text;
    userInput.focus();
    handleSendMessage();
}

// Send Message Handler
async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text || isProcessing) return;

    // Remove welcome card if present
    const welcome = document.getElementById("welcomeCard");
    if (welcome) welcome.remove();

    // Reset input
    userInput.value = "";
    userInput.style.height = "auto";
    isProcessing = true;
    sendBtn.disabled = true;

    // Append user message
    appendUserMessage(text);

    // Append typing indicator
    const typingIndicator = appendTypingIndicator();
    scrollToBottom();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                thread_id: currentThreadId
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Failed to generate answer");
        }

        const data = await response.json();
        
        // Remove typing indicator
        typingIndicator.remove();

        // Save current thread_id if provided by server
        if (data.thread_id) {
            currentThreadId = data.thread_id;
            threadDisplay.textContent = "Session: " + currentThreadId.substring(0, 15) + "...";
        }

        // Store message & chunks in history
        const msgIndex = messageHistory.length;
        messageHistory.push({
            userQuestion: text,
            answer: data.answer,
            retrieve: data.retrieve,
            ragQuery: data.rag_query,
            chunks: data.chunks || []
        });

        // Append assistant response
        appendAssistantMessage(data.answer, data.retrieve, data.rag_query, data.chunks || [], msgIndex);

        // Update chunks panel with latest retrieved items
        if (data.chunks && data.chunks.length > 0) {
            displayChunksInPanel(data.chunks, data.rag_query);
            // Open panel if closed
            chunksPanel.classList.remove("collapsed");
        } else {
            clearChunksPanel("No document chunks were retrieved for this conversational turn.");
        }

    } catch (err) {
        typingIndicator.remove();
        appendErrorMessage(err.message || "An error occurred while communicating with the assistant.");
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        userInput.focus();
        scrollToBottom();
    }
}

// Render User Message
function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row user";

    const body = document.createElement("div");
    body.className = "message-body";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    body.appendChild(bubble);
    row.appendChild(body);

    const avatar = document.createElement("div");
    avatar.className = "avatar user-avatar";
    avatar.innerHTML = '<i class="fa-solid fa-user"></i>';
    row.appendChild(avatar);

    chatMessages.appendChild(row);
    scrollToBottom();
}

// Render Assistant Message
function appendAssistantMessage(answer, retrieve, ragQuery, chunks, msgIndex) {
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const avatar = document.createElement("div");
    avatar.className = "avatar assistant-avatar";
    avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
    row.appendChild(avatar);

    const body = document.createElement("div");
    body.className = "message-body";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (typeof marked !== "undefined") {
        bubble.innerHTML = marked.parse(answer);
    } else {
        bubble.textContent = answer;
    }

    body.appendChild(bubble);

    // Meta footer under AI message
    const meta = document.createElement("div");
    meta.className = "message-meta";

    if (retrieve && chunks && chunks.length > 0) {
        const tag = document.createElement("span");
        tag.className = "meta-tag retrieved";
        tag.innerHTML = `<i class="fa-solid fa-check"></i> RAG Search (${chunks.length} chunks)`;
        meta.appendChild(tag);

        const inspectBtn = document.createElement("button");
        inspectBtn.className = "inspect-chunks-btn";
        inspectBtn.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> Inspect Chunks`;
        inspectBtn.onclick = () => {
            displayChunksInPanel(chunks, ragQuery);
            chunksPanel.classList.remove("collapsed");
        };
        meta.appendChild(inspectBtn);
    } else {
        const tag = document.createElement("span");
        tag.className = "meta-tag direct";
        tag.innerHTML = `<i class="fa-solid fa-comment-dots"></i> Direct Generation`;
        meta.appendChild(tag);
    }

    body.appendChild(meta);
    row.appendChild(body);

    chatMessages.appendChild(row);
    scrollToBottom();
}

// Render Typing Indicator
function appendTypingIndicator() {
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const avatar = document.createElement("div");
    avatar.className = "avatar assistant-avatar";
    avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
    row.appendChild(avatar);

    const body = document.createElement("div");
    body.className = "message-body";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble typing-bubble";
    bubble.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    body.appendChild(bubble);
    row.appendChild(body);

    chatMessages.appendChild(row);
    return row;
}

// Render Error Message
function appendErrorMessage(errorText) {
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const avatar = document.createElement("div");
    avatar.className = "avatar assistant-avatar";
    avatar.style.background = "var(--danger)";
    avatar.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
    row.appendChild(avatar);

    const body = document.createElement("div");
    body.className = "message-body";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.style.borderColor = "var(--danger)";
    bubble.innerHTML = `<p style="color: var(--danger); font-weight: 600;"><i class="fa-solid fa-circle-exclamation"></i> Error</p><p style="font-size: 0.9em; margin-top: 4px;">${escapeHtml(errorText)}</p>`;

    body.appendChild(bubble);
    row.appendChild(body);

    chatMessages.appendChild(row);
    scrollToBottom();
}

// Display Chunks in Inspector Panel
function displayChunksInPanel(chunks, ragQuery) {
    chunksCountBadge.textContent = chunks.length;
    ragQueryDisplay.textContent = ragQuery ? `"${ragQuery}"` : "Direct query";

    if (!chunks || chunks.length === 0) {
        clearChunksPanel("No document chunks retrieved for this turn.");
        return;
    }

    chunksList.innerHTML = "";

    chunks.forEach((chunk, idx) => {
        const card = document.createElement("div");
        card.className = "chunk-card";

        const scoreText = chunk.score !== null && chunk.score !== undefined ? `Score: ${chunk.score}` : "Score: N/A";
        const pageText = chunk.page_label && chunk.page_label !== "N/A" ? `Page ${chunk.page_label}` : "Page N/A";

        card.innerHTML = `
            <div class="chunk-header">
                <span class="chunk-index"><i class="fa-solid fa-file-lines"></i> Chunk #${idx + 1}</span>
                <div class="chunk-badges">
                    <span class="page-badge">${escapeHtml(pageText)}</span>
                    <span class="score-badge">${scoreText}</span>
                </div>
            </div>
            <div class="chunk-text-box" id="chunkText_${idx}">${escapeHtml(chunk.content || "")}</div>
            <div class="chunk-actions">
                <button class="chunk-btn" onclick="toggleExpandChunk(${idx})">
                    <i class="fa-solid fa-up-right-and-down-left-from-center" id="expandIcon_${idx}"></i> 
                    <span id="expandLabel_${idx}">Expand</span>
                </button>
                <button class="chunk-btn" onclick="copyChunkText(${idx})">
                    <i class="fa-regular fa-copy"></i> Copy
                </button>
            </div>
        `;

        chunksList.appendChild(card);
    });
}

function toggleExpandChunk(idx) {
    const box = document.getElementById(`chunkText_${idx}`);
    const icon = document.getElementById(`expandIcon_${idx}`);
    const label = document.getElementById(`expandLabel_${idx}`);
    if (box) {
        box.classList.toggle("expanded");
        const isExpanded = box.classList.contains("expanded");
        label.textContent = isExpanded ? "Collapse" : "Expand";
        icon.className = isExpanded 
            ? "fa-solid fa-down-left-and-up-right-to-center" 
            : "fa-solid fa-up-right-and-down-left-from-center";
    }
}

function copyChunkText(idx) {
    const box = document.getElementById(`chunkText_${idx}`);
    if (box) {
        navigator.clipboard.writeText(box.innerText).then(() => {
            const btn = box.parentElement.querySelector(".chunk-actions .chunk-btn:last-child");
            if (btn) {
                const orig = btn.innerHTML;
                btn.innerHTML = `<i class="fa-solid fa-check text-success"></i> Copied!`;
                setTimeout(() => { btn.innerHTML = orig; }, 1800);
            }
        });
    }
}

function clearChunksPanel(customMsg) {
    chunksCountBadge.textContent = "0";
    ragQueryDisplay.textContent = "No query executed yet.";
    chunksList.innerHTML = `
        <div class="empty-chunks">
            <i class="fa-solid fa-folder-open"></i>
            <p>${customMsg || "No chunks retrieved for this turn yet."}</p>
            <span>When you ask a question requiring document search, the retrieved passages and similarity scores will appear here.</span>
        </div>
    `;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
    initThread();
});
