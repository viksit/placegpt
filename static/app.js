const imageContainer = document.getElementById('image-container');

function fetchAndRenderImage() {
  const url = '/canvas?_=' + Date.now();

  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(imageData => {
      console.log("got imageData", imageData)
      // imageContainer.innerHTML = imageData;
      imageContainer.innerHTML = `<img src="${url}" alt="Canvas">`;
    })
    .catch(error => {
      console.error('There was a problem loading the image:', error);
    });
}

fetchAndRenderImage();

setInterval(fetchAndRenderImage, 1000);
