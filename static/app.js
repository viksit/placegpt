const svgContainer = document.getElementById('svg-container');

function fetchAndRenderSVG() {
  const url = '/canvas?_=' + Date.now();

  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(svgData => {
      svgContainer.innerHTML = svgData;
    })
    .catch(error => {
      console.error('There was a problem loading the SVG:', error);
    });
}

fetchAndRenderSVG();

setInterval(fetchAndRenderSVG, 1000);
