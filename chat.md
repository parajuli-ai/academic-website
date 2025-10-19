---
layout: page
title: AI Chat Assistant
permalink: /chat/
toc: false
---

<div class="chat-container" role="region" aria-label="AI Chat">
  <div class="chat-header">AI Assistant</div>
  <div id="chat-messages" class="chat-messages" aria-live="polite" aria-label="Chat messages">
    <div class="bot-message message">
      <div class="message-content">
        <p>👋 Hello! I'm an AI assistant trained on this academic profile.</p>
        <p>Try: <code>What are Tilak's research areas?</code> • <code>Summarize the gaze detection project</code> • <code>Link to the Meta Python certificate</code></p>
      </div>
    </div>
  </div>
  <div class="chat-input-container" id="chat-input-container">
    <label for="chat-input" class="sr-only">Type your message</label>
    <textarea id="chat-input" placeholder="Ask anything about research, projects, skills, or CV…" rows="2" aria-label="Chat input"></textarea>
    <button id="send-btn" aria-label="Send message">Send</button>
  </div>
  <div id="chat-status" class="loading" aria-live="polite" aria-atomic="true"></div>
</div>

---

> Tips: Press Enter to send, Shift+Enter for a newline. No data is stored.

<script src="{{ '/assets/js/chat.js' | relative_url }}"></script>

