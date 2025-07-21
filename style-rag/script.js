document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const loadingIndicator = document.getElementById('loading-indicator');
    const apiBaseUrl = 'http://127.0.0.1:8000';
    
    const fileInput = document.getElementById('file-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');

    let chatHistory = [];
    let conversationState = {};
    let selectedFile = null;

    displayMessage("Hello! I'm Genesis. Ask me about fashion, or upload an image to start a visual search.", "ai");

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = (event) => {
                imagePreview.src = event.target.result;
                imagePreviewContainer.style.display = 'flex';
            };
            reader.readAsDataURL(file);
        }
    });

    removeImageBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        imagePreviewContainer.style.display = 'none';
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMessage = messageInput.value.trim();
        if (!userMessage && !selectedFile) return;

        displayMessage(userMessage, 'user', [], selectedFile);
        chatHistory.push({ role: 'user', content: userMessage });
        
        const formData = new FormData();
        const chatRequest = { message: userMessage, history: chatHistory, state: conversationState };
        formData.append('chat_request_json', JSON.stringify(chatRequest));
        if (selectedFile) formData.append('image_file', selectedFile);

        messageInput.value = '';
        removeImageBtn.click();
        
        loadingIndicator.style.display = 'flex';
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const response = await fetch(`${apiBaseUrl}/api/chat`, { method: 'POST', body: formData });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            
            loadingIndicator.style.display = 'none';
            displayMessage(data.response, 'ai', data.items);
            
            chatHistory.push({ role: 'assistant', content: data.response });
            conversationState = data.state;
        } catch (error) {
            console.error('Error fetching from API:', error);
            loadingIndicator.style.display = 'none';
            displayMessage("Sorry, I'm having a little trouble connecting right now. Please try again.", 'ai');
        }
    });

    function displayMessage(message, sender, items = [], file = null) {
        const msgElement = document.createElement('div');
        msgElement.classList.add('chat-bubble', sender);

        if (sender === 'user' && file) {
            const userImg = document.createElement('img');
            userImg.src = URL.createObjectURL(file);
            userImg.style.maxHeight = '100px'; userImg.style.borderRadius = '8px'; userImg.style.marginBottom = '10px';
            msgElement.appendChild(userImg);
        }
        
        const textElement = document.createElement('p');
        textElement.style.margin = 0;
        textElement.textContent = message;
        msgElement.appendChild(textElement);

        if (items.length > 0) msgElement.appendChild(createItemsContainer(items));
        
        chatWindow.appendChild(msgElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function createItemsContainer(items) {
        const container = document.createElement('div');
        container.className = 'items-container';
        items.forEach(item => {
            const card = document.createElement('div'); card.className = 'product-card';
            const img = document.createElement('img'); img.src = `${apiBaseUrl}/images/${item.item_id}`;
            const content = document.createElement('div'); content.className = 'card-content';
            const title = document.createElement('div'); title.className = 'card-title'; title.textContent = item.category;
            const tagsDiv = document.createElement('div'); tagsDiv.className = 'card-tags';
            item.tags.slice(0, 3).forEach(tag => {
                const tagSpan = document.createElement('span'); tagSpan.className = 'tag'; tagSpan.textContent = tag;
                tagsDiv.appendChild(tagSpan);
            });
            content.appendChild(title); content.appendChild(tagsDiv);
            card.appendChild(img); card.appendChild(content);
            container.appendChild(card);
        });
        return container;
    }
});