/**
 * Chat Interface JavaScript
 * Handles communication with the RAG backend
 */

(function() {
    'use strict';
    
    // Get API URL from Jekyll config or use default
    // const API_URL = typeof chatApiUrl !== 'undefined' ? chatApiUrl : 'http://localhost:8001';
    const API_URL = typeof chatApiUrl !== 'undefined' ? chatApiUrl : 'https://academic-website-backend.onrender.com';
    
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatStatus = document.getElementById('chat-status');
    
    if (!chatMessages || !chatInput || !sendBtn) {
        console.error('Chat elements not found');
        return;
    }
    
    // Initialize chat
    function init() {
        sendBtn.addEventListener('click', handleSendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
        
        // Focus input on load
        chatInput.focus();
    }
    
    // Handle sending a message
    async function handleSendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Disable input while processing
        setInputEnabled(false);
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatInput.value = '';
        
        // Show loading status
        setStatus('Thinking...');
        
        try {
            // Send request to backend
            const response = await sendChatRequest(message);
            
            // Add bot response
            addMessage(response, 'bot');
            
            // Clear status
            setStatus('');
            
        } catch (error) {
            console.error('Chat error:', error);
            
            // Show error message
            const errorMessage = getErrorMessage(error);
            addMessage(errorMessage, 'bot');
            
            setStatus('');
        } finally {
            // Re-enable input
            setInputEnabled(true);
            chatInput.focus();
        }
    }
    
    // Send chat request to backend
    async function sendChatRequest(message) {
        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: message,
                    conversation_id: 'web_chat_' + Date.now()
                })
            });
            
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('RATE_LIMIT');
                } else if (response.status === 503) {
                    throw new Error('SERVICE_UNAVAILABLE');
                } else if (response.status === 500) {
                    throw new Error('API_ERROR');
                } else {
                    throw new Error('API_ERROR');
                }
            }
            
            const data = await response.json();
            
            // Format response with sources if available
            let responseText = data.answer || 'Sorry, I could not generate a response.';
            
            // Add sources if available
            if (data.sources && data.sources.length > 0) {
                responseText += '\n\n**Sources:**\n';
                data.sources.forEach((source, idx) => {
                    const confidence = Math.round(source.score * 100);
                    responseText += `${idx + 1}. ${source.metadata.filename} (${confidence}% confidence)\n`;
                });
            }
            
            return responseText;
            
        } catch (error) {
            if (error.name === 'TypeError') {
                throw new Error('NETWORK_ERROR');
            }
            throw error;
        }
    }
    
    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Convert markdown-like formatting to HTML
        const formattedText = formatMessage(text);
        contentDiv.innerHTML = formattedText;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Format message text (basic markdown support)
    function formatMessage(text) {
        // Escape HTML
        let formatted = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Bold
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Code
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Links (basic)
        formatted = formatted.replace(
            /\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return formatted;
    }
    
    // Get user-friendly error message
    function getErrorMessage(error) {
        const errorType = error.message;
        
        const messages = {
            'RATE_LIMIT': '⚠️ Too many requests. Please wait a moment and try again.',
            'SERVICE_UNAVAILABLE': '⚠️ The chat service is temporarily unavailable. Please try again later.',
            'API_ERROR': '⚠️ An error occurred while processing your request. Please try again.',
            'NETWORK_ERROR': '⚠️ Network error. Please check your connection and try again.'
        };
        
        return messages[errorType] || messages['API_ERROR'];
    }
    
    // Set status message
    function setStatus(message) {
        if (message) {
            chatStatus.innerHTML = `<span class="loading-dots">${message}</span>`;
        } else {
            chatStatus.innerHTML = '';
        }
    }
    
    // Enable/disable input controls
    function setInputEnabled(enabled) {
        chatInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();

// Alternative: Floating chat widget (optional)
// Uncomment to add a floating chat button

/*
function createFloatingChatWidget() {
    const chatWidget = document.createElement('div');
    chatWidget.id = 'floating-chat-widget';
    chatWidget.innerHTML = `
        <button id="chat-toggle-btn" aria-label="Open chat">
            💬
        </button>
        <div id="floating-chat-container" style="display: none;">
            <div id="floating-chat-header">
                <span>AI Assistant</span>
                <button id="close-chat-btn" aria-label="Close chat">×</button>
            </div>
            <div id="floating-chat-messages"></div>
            <div id="floating-chat-input-container">
                <input type="text" id="floating-chat-input" placeholder="Ask a question...">
                <button id="floating-send-btn">Send</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(chatWidget);
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        #floating-chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        #chat-toggle-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            border: none;
            font-size: 2em;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        #floating-chat-container {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
        }
        
        #floating-chat-header {
            background-color: var(--primary-color);
            color: white;
            padding: 1rem;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        #close-chat-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5em;
            cursor: pointer;
        }
        
        #floating-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }
        
        #floating-chat-input-container {
            display: flex;
            padding: 1rem;
            border-top: 1px solid #ddd;
        }
        
        #floating-chat-input {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 0.5rem;
        }
        
        #floating-send-btn {
            padding: 0.5rem 1rem;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    `;
    document.head.appendChild(style);
    
    // Add event listeners
    document.getElementById('chat-toggle-btn').addEventListener('click', () => {
        const container = document.getElementById('floating-chat-container');
        container.style.display = container.style.display === 'none' ? 'flex' : 'none';
    });
    
    document.getElementById('close-chat-btn').addEventListener('click', () => {
        document.getElementById('floating-chat-container').style.display = 'none';
    });
}

// Uncomment to enable floating widget
// if (window.location.pathname !== '/chat') {
//     createFloatingChatWidget();
// }
*/

