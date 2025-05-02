window.onload = function() {
  const ledBuilding = document.getElementById('ledBuilding');
  // const textBox = document.getElementById('textBox');

  // Create WebSocket connection for the text box
  // const textBoxWS = new WebSocket('ws://localhost:9001');

  // textBoxWS.onopen = function() {
  //   console.log(`WebSocket connection for text box established.`);
  // };

  // textBoxWS.onmessage = function(event) {
  //   const data = event.data;
  //   console.log(data);

  //   // Display received message in the text box
  //   textBox.value = data;
  // };

  // textBoxWS.onclose = function() {
  //   console.log(`WebSocket connection for text box closed.`);
  // };


  // Create LED blocks
  //5 by 11
  for (let row = 0; row < 5; row++) {
    for (let column = 0; column < 11; column++) {
      const ledBlock = document.createElement('div');
      ledBlock.classList.add('ledBlock');

      ledBlock.setAttribute('row', row); // Set 'row' attribute
      ledBlock.setAttribute('column', column); // Set 'col' attribute

      ledBlock.dataset.row = row;
      ledBlock.dataset.column = column;
      ledBuilding.appendChild(ledBlock);

      // ledBlock.dataset.color1 = "#000000";
      // ledBlock.dataset.color2 = "#FF0000";

      // Create WebSocket connection for each LED block
      //const ws = new WebSocket('ws://localhost:9001');
      const ws = new WebSocket('wss://kazar4.com:9001')

      ws.onopen = function() {
        console.log(`WebSocket connection for LED block (${row}, ${column}) established.`);
        // Send message to WebSocket server to identify LED block
        ws.send(`M-${row}-${column}`);
      };

      ws.onmessage = function(event) {
        const data = event.data;
        console.log(data);

        //Example: Change color of LED block based on received data
        if (data === 'ping') {
          ws.send('pong');
        }

        if (data.includes('info')) {
          ws.send("info " + JSON.stringify({"type": "info", "esp": data.split(":")[1],"firmware": "nonESPSimulation"}));
        }

        // $2-1#FF00FF

        if (data[0] === '$' && data.length >= 10) {
          console.log('Setting color to:', data);
        
          const numOfLeds = parseInt(data[1]);
          const ledChosen = parseInt(data[3]);
          const colorVal = data.substring(4); // e.g. #FF00FF
        
          // Clamp LED index
          if (ledChosen > numOfLeds) {
            ledBlock.dataset.colors = JSON.stringify(Array(numOfLeds).fill(colorVal));
            ledBlock.setAttribute("style", `background: ${colorVal};`);
            return;
          }
        
          // Get or initialize colors array
          let colors = ledBlock.dataset.colors
            ? JSON.parse(ledBlock.dataset.colors)
            : Array(numOfLeds).fill("#000000");
        
          // Ensure it's exactly the right length
          if (colors.length !== numOfLeds) {
            const newColors = Array(numOfLeds).fill("#000000");
            for (let i = 0; i < Math.min(colors.length, numOfLeds); i++) {
              newColors[i] = colors[i] || "#000000";
            }
            colors = newColors;
          }
        
          // Update color
          colors[ledChosen - 1] = colorVal;
          ledBlock.dataset.colors = JSON.stringify(colors);
        
          // Build gradient from numOfLeds entries only
          const step = 100 / numOfLeds;
          const gradientParts = colors.map((color, i) => {
            const start = i * step;
            const end = start + step;
            return `${color} ${start}%, ${color} ${end}%`;
          });
        
          const gradient = `linear-gradient(90deg, ${gradientParts.join(', ')})`;
          console.log("Setting gradient:", gradient);
        
          ledBlock.style.background = gradient;
          ledBlock.setAttribute("style", `background: ${gradient};`);
        }
      };

      ws.onclose = function() {
        console.log(`WebSocket connection for LED block (${row}, ${column}) closed.`);
      };
    }
    // Add a line break after each row of LED blocks
  }
};
