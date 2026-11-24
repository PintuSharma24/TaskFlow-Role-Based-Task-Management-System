
const CHATBOT_API_URL = "http://127.0.0.1:8000/api/v1/chatbot/ask";

document.addEventListener("DOMContentLoaded", async function () {

    // 1. Load chatbot CSS
    const chatbotCSS = document.createElement("link");
    chatbotCSS.rel = "stylesheet";
    chatbotCSS.href = "../css/chatbot.css";
    document.head.appendChild(chatbotCSS);

    // 2. Load chatbot HTML
    try {
        const response = await fetch("../components/chatbot.html");

        if (!response.ok) {
            throw new Error("Unable to load chatbot component.");
        }

        const chatbotHTML = await response.text();
        document.body.insertAdjacentHTML("beforeend", chatbotHTML);

        // 3. Get chatbot elements
        const chatbotToggle = document.getElementById("chatbotToggle");
        const chatbotClose = document.getElementById("chatbotClose");
        const chatbotWindow = document.getElementById("chatbotWindow");
        const chatInput = document.getElementById("chatbotInput");
        const sendButton = document.getElementById("chatbotSend");
        const messagesContainer = document.getElementById("chatbotMessages");


        // Open chatbot
        chatbotToggle.addEventListener("click", () => {
        chatbotWindow.style.setProperty("display", "flex", "important");
        chatbotToggle.style.setProperty("display", "none", "important");
        });

        // Close chatbot
        chatbotClose.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();

        chatbotWindow.style.setProperty("display", "none", "important");
        chatbotToggle.style.setProperty("display", "flex", "important");
        });

       
        // 6. Add messages safely
        function addMessage(message, sender) {

            const messageWrapper = document.createElement("div");
            messageWrapper.classList.add("chat-message");

            messageWrapper.classList.add(
                sender === "user" ? "user-message" : "bot-message"
            );

            const avatar = document.createElement("div");
            avatar.classList.add("message-avatar");
            avatar.textContent = sender === "user" ? "👤" : "🤖";

            const messageContent = document.createElement("div");
messageContent.classList.add("message-content");

            // Convert escaped newlines into actual newlines
            const formattedMessage = message
            .replace(/\\n/g, "\n")
            .replace(/\r\n/g, "\n");

            // Force the browser to preserve line breaks
            messageContent.style.whiteSpace = "pre-wrap";
            messageContent.style.overflowWrap = "anywhere";

            messageContent.textContent = formattedMessage;

            messageWrapper.appendChild(avatar);
            messageWrapper.appendChild(messageContent);

            messagesContainer.appendChild(messageWrapper);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            return messageWrapper;
        }

        // 7. Send message to FastAPI RAG chatbot
        async function sendMessage() {

            const message = chatInput.value.trim();

            if (!message || sendButton.disabled) {
                return;
            }

            const token = localStorage.getItem("access_token");

            if (!token) {
                addMessage(
                    "Your session has expired. Please log in again.",
                    "bot"
                );
                return;
            }
            // Display user's message
            addMessage(message, "user");

            chatInput.value = "";
            sendButton.disabled = true;

            // Show loading message
            const loadingMessage = addMessage(
                "Thinking... Please wait.",
                "bot"
            );

            try {

                const response = await fetch(CHATBOT_API_URL, {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        message: message
                    })
                });

                const result = await response.json();

                // Remove loading message
                loadingMessage.remove();

                if (!response.ok) {

                    if (response.status === 401) {
                        throw new Error("Session expired. Please log in again.");
                    }

                    if (response.status === 403) {
                        throw new Error("Only authorized Managers can use this chatbot.");
                    }

                    throw new Error(
                        result.detail || "Unable to get an AI response."
                    );
                }

                // Display AI-generated answer
                addMessage(result.answer, "bot");

                // Display retrieved source references

                // Display sources for RAG answers.
                // Employee reports come directly from SQL, so their source message is unnecessary.
                if (result.sources && result.sources.length > 0) {
                    const visibleSources = result.sources.filter(
                        source => source.source_type !== "employee_report");
                        if (visibleSources.length > 0) {
                            const sourceText = visibleSources
                            .map(source => `${source.source_type} - ID ${source.source_id}`)
                            .join("\n");
                            
                        addMessage("Retrieved sources:\n" + sourceText, "bot");}
}

            } catch (error) {

                loadingMessage.remove();

                addMessage(
                    error.message || "Something went wrong. Please try again.",
                    "bot"
                );

                console.error("TaskFlow chatbot error:", error);

            } finally {

                sendButton.disabled = false;
                chatInput.focus();

            }
        }

        // 8. Send button
        sendButton.addEventListener("click", sendMessage);

        // 9. Enter to send, Shift + Enter for newline
        chatInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }

        });

        console.log("TaskFlow AI chatbot connected successfully.");

    } catch (error) {

        console.error("Chatbot initialization failed:", error);

    }

});
