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

      ledBlock.dataset.color1 = "#000000";
      ledBlock.dataset.color2 = "#FF0000";

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

        if (data !== undefined && data !== null && data[0] === '$' && data.length === 9) {
          console.log('Setting color to: ' + data);
          
          if (data[1] == 1) {
            ledBlock.dataset.color1 = data.substring(2);
          } else if (data[1] == 2) {
            ledBlock.dataset.color2 = data.substring(2);
          } else {
            ledBlock.dataset.color1 = data.substring(2);
            ledBlock.dataset.color2 = data.substring(2);
          }

          console.log("TRYING TO SET THESE")
          console.log(ledBlock.dataset.color1)
          console.log(ledBlock.dataset.color2)
          console.log(`linear-gradient(90deg, ${ledBlock.dataset.color1} 50%, ${ledBlock.dataset.color2} 50%);`)
          ledBlock.style.background = `linear-gradient(90deg, ${ledBlock.dataset.color1} 50%, ${ledBlock.dataset.color2} 50%);`
          ledBlock.setAttribute("style", `background:linear-gradient(90deg, ${ledBlock.dataset.color1} 50%, ${ledBlock.dataset.color2} 50%);`);
          //data.substring(2);
          //background: linear-gradient(90deg, #FFC0CB 50%, #00FFFF 50%);
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
