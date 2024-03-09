function setPredominantBackgroundColor(imageElement, containerElement) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const img = new Image();

    img.onload = function () {
        // Set canvas size to the image size
        canvas.width = this.width;
        canvas.height = this.height;
        context.drawImage(this, 0, 0, this.width, this.height);

        // Get image data
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        const colorMap = {};

        // Generate a color map with frequency of each color
        for (let i = 0; i < data.length; i += 4) {
            // Convert color to a string in the form of 'r,g,b'
            const color = `${data[i]},${data[i + 1]},${data[i + 2]}`;

            if (colorMap[color]) {
                colorMap[color]++;
            } else {
                colorMap[color] = 1;
            }
        }

        // Determine the most frequent color
        let predominantColor = { color: null, count: 0 };
        for (const [color, count] of Object.entries(colorMap)) {
            if (count > predominantColor.count) {
                predominantColor = { color, count };
            }
        }

        // Set container background to predominant color
        containerElement.style.backgroundColor = `rgb(${predominantColor.color})`;
        new_color = predominantColor.color;
        var r = new_color.r;
        var g = new_color.g;
        var b = new_color.b;
        var yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        containerElement.style.color = rgb(yiq, yiq, yiq);
    };

    // Handle CORS security if the images are not served from the same domain
    img.crossOrigin = 'Anonymous';

    // Start loading the image
    img.src = imageElement.src;
}
