const API_BASE_URL = "http://127.0.0.1:8000";
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");

// Session ID for context
const sessionId = "session_" + Math.random().toString(36).substr(2, 9);

async function updateDashboard() {
    try {
        // Fetch tasks
        const tasksRes = await fetch(`${API_BASE_URL}/tasks`);
        if (tasksRes.ok) {
            const tasks = await tasksRes.json();
            const total = tasks.length;
            const completed = tasks.filter(t => t.completed).length;
            const pending = total - completed;
            
            document.getElementById("totalTasks").textContent = total;
            document.getElementById("completedTasks").textContent = completed;
            document.getElementById("pendingTasks").textContent = pending;
        }

        // Fetch reminders
        const remRes = await fetch(`${API_BASE_URL}/reminders`);
        if (remRes.ok) {
            const reminders = await remRes.json();
            const remList = document.getElementById("reminderList");
            remList.innerHTML = "";
            if (reminders.length === 0) {
                remList.innerHTML = "<li>No upcoming reminders</li>";
            } else {
                reminders.forEach(r => {
                    const date = new Date(r.reminder_time);
                    const formatted = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + " " + date.toLocaleDateString();
                    remList.innerHTML += `<li>${r.message}<br><small style="color:var(--text-muted)">${formatted}</small></li>`;
                });
            }
        }
    } catch (e) {
        console.error("Dashboard update failed:", e);
    }
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    
    appendMessage(text, "user");
    userInput.value = "";
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text, session_id: sessionId })
        });
        
        if (response.ok) {
            const data = await response.json();
            appendMessage(data.response, "assistant");
            updateDashboard();
        } else {
            appendMessage("Sorry, I encountered an error while processing that.", "system");
        }
    } catch (error) {
        console.error(error);
        appendMessage("Network error: Could not connect to EchoMind AI.", "system");
    }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

// Voice Recognition
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = function() {
        voiceBtn.classList.add("recording");
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
        voiceBtn.classList.remove("recording");
        if (event.error !== 'no-speech') {
            appendMessage("Voice input failed. Please type your message.", "system");
        }
    };

    recognition.onend = function() {
        voiceBtn.classList.remove("recording");
    };
} else {
    voiceBtn.style.display = 'none'; // Hide if not supported
}

voiceBtn.addEventListener("click", () => {
    if (recognition) {
        if (voiceBtn.classList.contains("recording")) {
            recognition.stop();
        } else {
            recognition.start();
        }
    } else {
        appendMessage("Voice recognition is not supported in this browser.", "system");
    }
});

// Initial dashboard load
updateDashboard();
