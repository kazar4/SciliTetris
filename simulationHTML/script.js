window.onload = function() {
  const ledBuilding = document.getElementById('ledBuilding');
  const textBox = document.getElementById('textBox');

  // Create WebSocket connection for the text box
  const textBoxWS = new WebSocket('ws://localhost:9001');

  textBoxWS.onopen = function() {
    console.log(`WebSocket connection for text box established.`);
  };

  textBoxWS.onmessage = function(event) {
    const data = event.data;
    console.log(data);

    // Display received message in the text box
    textBox.value = data;
  };

  textBoxWS.onclose = function() {
    console.log(`WebSocket connection for text box closed.`);
  };

  // Create LED blocks
  for (let row = 0; row < 5; row++) {
    for (let column = 0; column < 14; column++) {
      const ledBlock = document.createElement('div');
      ledBlock.classList.add('ledBlock');

      ledBlock.setAttribute('row', row); // Set 'row' attribute
      ledBlock.setAttribute('column', column); // Set 'col' attribute

      ledBlock.dataset.row = row;
      ledBlock.dataset.column = column;
      ledBuilding.appendChild(ledBlock);

      // Create WebSocket connection for each LED block
      // const ws = new WebSocket('wss://kazar4.com:9001');
      const ws = new WebSocket('ws://localhost:9001')

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

        if (data !== undefined && data !== null && data[0] === '#' && data.length === 7) {
          console.log('Setting color to: ' + data);
          ledBlock.style.backgroundColor = data;
          // Logic to set color of corresponding LED block
        }
      };

      ws.onclose = function() {
        console.log(`WebSocket connection for LED block (${row}, ${column}) closed.`);
      };
    }
    // Add a line break after each row of LED blocks
  }
};
