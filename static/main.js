function setPredominantBackgroundColor(imageElement, containerElement) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const img = new Image();

        img.onload = function () {
            canvas.width = this.width;
            canvas.height = this.height;
            context.drawImage(this, 0, 0, this.width, this.height);

            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            const colorMap = {};

            for (let i = 0; i < data.length; i += 4) {
                const color = `${data[i]},${data[i + 1]},${data[i + 2]}`;
                colorMap[color] = (colorMap[color] || 0) + 1;
            }

            let predominantColor = { color: null, count: 0 };
            for (const [color, count] of Object.entries(colorMap)) {
                if (count > predominantColor.count) {
                    predominantColor = { color, count };
                }
            }

            containerElement.style.backgroundColor = `rgb(${predominantColor.color})`;

            const rgbValues = predominantColor.color.split(',').map(Number);
            const contrastColor = getContrastYIQ({ r: rgbValues[0], g: rgbValues[1], b: rgbValues[2] });

            resolve({ predominantColor: `rgb(${predominantColor.color})`, contrastColor });
        };

        img.onerror = reject;

        img.crossOrigin = 'Anonymous';
        img.src = imageElement.src;
    });
}

function getContrastYIQ({ r, g, b }) {
    const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
    return (yiq >= 128) ? 'black' : 'white';
}
