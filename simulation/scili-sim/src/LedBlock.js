import React, { useState, useEffect } from 'react';

const LedBlock = ({ row, column }) => {
  const [isOn, setIsOn] = useState(false);

  const [color, setColor] = useState("#000000")

  useEffect(() => {
    const ws = new WebSocket('wss://kazar4.com:9001');

    ws.onopen = (event) => {
      ws.send("M-asdqsd");
    };

    ws.onmessage = (event) => {
      // Handle messages received from the WebSocket server
      const data = event.data

      console.log(data);
      
      if (data != undefined && data != null && data[0] == "#" && data.length == 7) {
        console.log("Setting color to: " + data);
        setColor(data);
      }

      //JSON.parse(event.data);
      // Example: If the message indicates that this LED block should be turned on
    //   if (data.row === row && data.column === column) {
    //     setIsOn(true);
    //   }
    };

    // Cleanup function
    return () => {
      ws.close();
    };
  }, [row, column]);

  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        background: color,
        border: '1px solid white',
      }}
    />
  );
};

export default LedBlock;