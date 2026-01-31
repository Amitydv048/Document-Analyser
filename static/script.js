document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileElem = document.getElementById('fileElem');
    const uploadSection = document.getElementById('upload-section');
    const chatSection = document.getElementById('chat-section');
    const uploadLoader = document.getElementById('upload-loader');
    const docStatus = document.getElementById('doc-status');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    dropArea.addEventListener('click', () => fileElem.click());
    fileElem.addEventListener('change', (e) => handleFiles(e.target.files));

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }

    async function uploadFile(file) {
        // Show loader
        dropArea.style.display = 'none';
        uploadLoader.classList.remove('hidden');

        let formData = new FormData();
        formData.append('file', file);

        try {
            let response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                let result = await response.json();

                // Update UI
                docStatus.innerHTML = `<span>📄 ${result.filename}</span>`;
                docStatus.classList.remove('empty');

                uploadSection.style.display = 'none';
                chatSection.classList.remove('hidden');
            } else {
                alert('Upload failed. Please try again.');
                dropArea.style.display = 'block';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during upload.');
            dropArea.style.display = 'block';
        } finally {
            uploadLoader.classList.add('hidden');
        }
    }

    // Chat functionality
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, 'user');
        userInput.value = '';

        // Add loading placeholder
        const loadingId = addMessage('Thinking...', 'bot', true);

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: text })
            });

            const data = await response.json();

            // Remove loading and add real response
            removeMessage(loadingId);
            addMessage(data.answer, 'bot');

        } catch (error) {
            console.error('Error:', error);
            removeMessage(loadingId);
            addMessage('Sorry, I encountered an error.', 'bot');
        }
    }

    function addMessage(text, type, isLoading = false) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', type);

        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        bubble.textContent = text;

        if (isLoading) {
            msgDiv.id = 'loading-' + Date.now();
            bubble.style.opacity = '0.7';
        }

        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        return msgDiv.id;
    }

    function removeMessage(id) {
        const msg = document.getElementById(id);
        if (msg) msg.remove();
    }
});
