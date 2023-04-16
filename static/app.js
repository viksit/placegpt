const imageContainer = document.getElementById('image-container');
const imgElement = document.createElement('img');
imgElement.alt = 'Canvas';
imageContainer.appendChild(imgElement);

const chatContainer = document.getElementById('chat-container');

function updateContent() {
  // Update image
  const imageUrl = '/canvas?_=' + Date.now();
  const tempImg = new Image();
  tempImg.src = imageUrl;
  tempImg.onload = () => {
    imgElement.classList.add('fade-out');
    imgElement.classList.add('image-canvas');
    setTimeout(() => {
      imgElement.src = tempImg.src;
      imgElement.classList.remove('fade-out');
    }, 300);
  };

  // Update chat history
  fetch('/history?_=' + Date.now())
    .then(response => response.json())
    .then(chatHistory => {
      const tempChatContainer = document.createElement('div');

      // Render each chat message as a div within the temporary chat container
      chatHistory.forEach(chatMessage => {
        const chatMessageDiv = document.createElement('div');
        chatMessageDiv.textContent = chatMessage;
        tempChatContainer.appendChild(chatMessageDiv);
      });

      // Replace the chat container's contents with the new messages
      chatContainer.innerHTML = tempChatContainer.innerHTML;
    })
    .catch(error => {
      console.error('There was a problem fetching chat history:', error);
    });
}

updateContent();

setInterval(updateContent, 1000); // Update both image and chat history every 1000 ms
