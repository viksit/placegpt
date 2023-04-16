const imageContainer = document.getElementById('image-container');
const imgElement = document.createElement('img');
imgElement.alt = 'Canvas';
imageContainer.appendChild(imgElement);

function updateImage() {
  const url = '/canvas?_=' + Date.now();

  const tempImg = new Image();
  tempImg.src = url;
  tempImg.onload = () => {
    imgElement.classList.add('fade-out');
    imgElement.classList.add('image-canvas');
    setTimeout(() => {
      imgElement.src = tempImg.src;
      imgElement.classList.remove('fade-out');
    }, 300);
  };
}

updateImage();

setInterval(updateImage, 1000);
