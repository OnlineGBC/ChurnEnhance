document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Add user message
        appendMessage('user', text);
        input.value = '';

        // Add loading indicator
        const loadingEl = appendMessage('assistant', '<span class="text-gray-400 animate-pulse">Thinking...</span>');

        try {
            const response = await fetch('/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            loadingEl.querySelector('.msg-content').innerHTML = formatMessage(data.response || data.error || 'No response');
        } catch (err) {
            loadingEl.querySelector('.msg-content').innerHTML = '<span class="text-red-500">Error: ' + err.message + '</span>';
        }

        messages.scrollTop = messages.scrollHeight;
    });

    function appendMessage(role, content) {
        const wrapper = document.createElement('div');
        wrapper.className = 'flex gap-3' + (role === 'user' ? ' justify-end' : '');

        if (role === 'assistant') {
            wrapper.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-brand-primary flex items-center justify-center flex-shrink-0">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                </div>
                <div class="bg-white rounded-lg border border-gray-200 px-4 py-3 max-w-2xl">
                    <div class="text-sm text-gray-700 msg-content">${content}</div>
                </div>`;
        } else {
            wrapper.innerHTML = `
                <div class="bg-brand-primary text-white rounded-lg px-4 py-3 max-w-2xl">
                    <div class="text-sm msg-content">${content}</div>
                </div>
                <div class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                    <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                </div>`;
        }

        messages.appendChild(wrapper);
        messages.scrollTop = messages.scrollHeight;
        return wrapper;
    }

    function formatMessage(text) {
        // Basic markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }
});
