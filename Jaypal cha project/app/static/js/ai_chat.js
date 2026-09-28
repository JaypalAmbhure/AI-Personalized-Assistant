// Interactive AI Financial Advisor & Audit Trigger Scripts

document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    function appendMessage(text, sender = 'user') {
        if (!chatMessages) return;

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;

        // Basic Markdown parsing for clean presentation
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/^### (.*$)/gim, '<h6 class="fw-bold text-white mt-2 mb-1">$1</h6>')
            .replace(/^#### (.*$)/gim, '<h6 class="fw-bold text-primary mt-2 mb-1">$1</h6>')
            .replace(/^\- (.*$)/gim, '<li class="ms-2">$1</li>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');

        bubble.innerHTML = formatted;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'chat-bubble assistant text-muted fst-italic';
        indicator.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i> FinAura AI is evaluating your finances...';
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    if (chatForm && chatInput) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            appendMessage(message, 'user');
            chatInput.value = '';
            showTypingIndicator();

            fetch('/ai-advisor/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
                .then(res => res.json())
                .then(data => {
                    removeTypingIndicator();
                    if (data.reply) {
                        appendMessage(data.reply, 'assistant');
                    } else {
                        appendMessage("Sorry, I couldn't process that query. Please try again.", 'assistant');
                    }
                })
                .catch(err => {
                    removeTypingIndicator();
                    appendMessage("Network error communicating with AI Advisor.", 'assistant');
                });
        });
    }

    // AI Generation Triggers
    window.triggerAIGeneration = function (endpoint, resultContainerId, btn) {
        const container = document.getElementById(resultContainerId);
        if (!container) return;

        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> Generating Plan...';
        btn.disabled = true;

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => res.json())
            .then(data => {
                btn.innerHTML = originalText;
                btn.disabled = false;

                if (data.content) {
                    let formatted = data.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/`([^`]+)`/g, '<span class="badge bg-dark text-info">$1</span>')
                        .replace(/^### (.*$)/gim, '<h5 class="fw-bold text-white mt-3 mb-2">$1</h5>')
                        .replace(/^#### (.*$)/gim, '<h6 class="fw-bold text-indigo mt-3 mb-1 text-primary">$1</h6>')
                        .replace(/^\- (.*$)/gim, '<li class="ms-3 mb-1">$1</li>')
                        .replace(/\n\n/g, '<p class="mb-2"></p>')
                        .replace(/\n/g, '<br>');

                    container.innerHTML = `
                        <div class="glass-card mb-4 border-glow">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold text-white mb-0"><i class="fa-solid fa-sparkles text-primary me-2"></i>${data.title}</h5>
                                <span class="badge badge-soft-indigo">${data.created_at}</span>
                            </div>
                            <div class="text-light" style="font-size: 0.95rem; line-height: 1.6;">
                                ${formatted}
                            </div>
                        </div>
                    `;
                    container.scrollIntoView({ behavior: 'smooth' });
                }
            })
            .catch(err => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert('Error generating AI recommendation.');
            });
    };
});
