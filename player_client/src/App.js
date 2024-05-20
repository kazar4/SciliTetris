import {React, useState, useEffect} from 'react';
import { Box, Button, VStack, HStack } from '@chakra-ui/react';

function App() {
  const [ws, setWS] = useState(null)
  const [wsRes, setWsRes] = useState(null);

  useEffect(() => {
    // const websocket = new WebSocket('wss://kazar4.com:9001');
    const websocket = new WebSocket('ws://localhost:9001')

    websocket.onopen = () => {
      console.log('WebSocket connection established.');
      setWS(websocket); // Store WebSocket connection in state
      websocket.send("player")
    };
    websocket.onclose = () => {
      console.log('WebSocket connection closed.');
    };
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log(message)
      setWsRes(message);
    };
    return () => {
      // Close WebSocket connection when component unmounts
      if (ws) {
        console.log("websocket is closing, i'm not sure why")
        ws.close();
      }
    };
  }, []); // Empty dependency array ensures this effect runs only once on component mount

  return (
    <Box className="gamepad" h="300px" d="flex" alignItems="center" justifyContent="center">
      <VStack spacing="5">

        <Button className="button up" size="lg" onClick={() => {
          if (ws) {
            ws.send("playerInput up")
          }
        }}
        >Up</Button>

        <HStack spacing="5">

          <Button className="button left" size="lg" onClick={() => {
          if (ws) {
            ws.send("playerInput left")
          }
        }}>Left</Button>

          <Button className="button right" size="lg" onClick={() => {
          if (ws) {
            ws.send("playerInput right")
          }
        }}>Right</Button>

        </HStack>

        <Button className="button down" size="lg" onClick={() => {
          if (ws) {
            ws.send("playerInput down")
          }
        }}>Down</Button>

      </VStack>
    </Box>
  );
}

export default App;
