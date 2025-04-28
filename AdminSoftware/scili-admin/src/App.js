import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Box,
  Text,
  theme,
  Flex,
  Textarea,
} from '@chakra-ui/react';
import { ColorModeSwitcher } from './ColorModeSwitcher';
// import { Logo } from './archive/Logo';
// import LedBuilding from './LedBuilding';
import LedDisplay from './LedDisplay';
import EspClientList from './ESPClientList';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { DndProvider } from 'react-dnd';
import { ControlsPane } from './ControlsPane';

function App() {

  const [ws, setWs] = useState(null); // WebSocket connection
  const [wsRes, setWsRes] = useState(null);

  const [reconnect, setReconnect] = useState(1);

  const [mode, setMode] = useState("");
  const [hexCode, setHexCode] = useState('');
  const [strip, setStrip] = useState('3');
  const [syncDelay, setSyncDelay] = useState("");

  const [xDimension, setXDimension] = useState(5); // Initial x dimension
  const [yDimension, setYDimension] = useState(11); // Initial y dimension

  const textBoxRef = React.createRef();




  useEffect(() => {
   // const websocket = new WebSocket('wss://proteinarium.brown.edu:4567');
    const websocket = new WebSocket('wss://kazar4.com:9001')
    // const websocket = new WebSocket('ws://localhost:9001')

    websocket.onopen = () => {
      console.log('WebSocket connection established.');
      setWs(websocket); // Store WebSocket connection in state
      websocket.send("admin")
      websocket.send("getClientState")
    };
    websocket.onclose = () => {
      console.log('WebSocket connection closed.');
      setReconnect(reconnect + 1);
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
  }, [reconnect]); // Empty dependency array ensures this effect runs only once on component mount


  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">

      {/* <Flex alignContent={"center"} justifyContent={"center"} mt={"10%"}> */}
        {/* <LedBuilding></LedBuilding> */}

        {/* <DndProvider backend={HTML5Backend}>

          <LedDisplay ws={ws} wsRes={wsRes}></LedDisplay>

          <LedPopup></LedPopup>

          <EspClientList ws={ws} wsRes={wsRes}></EspClientList>

        </DndProvider> */}
      {/* </Flex> */}

      <DndProvider backend={HTML5Backend}>
        <Flex direction="column" height="100vh">
        {/* Top section */}
        <Flex justify="space-between" align="center" height="10%">
        <ColorModeSwitcher justifySelf="flex-end" />
          <Box flex="0 0 20%"></Box>
          <Box flex="0 0 60%" textAlign="center">Scili Admin Controls</Box>
          <Box flex="0 0 20%" textAlign="right"></Box>
        </Flex>
        
        {/* Main Section */}
        <Flex height="60%">

          {/* Left Section */}
          {/* *********** CONTROLS ************ */}
          <Box flex="0 0 30%">  
            <Text mb={6}>Controls</Text>
            <ControlsPane 
              ws={ws} 
              mode={mode} 
              setMode={setMode}
              setHexCode={setHexCode}
              setStrip={setStrip}
              setSyncDelay={setSyncDelay}
              syncDelay={syncDelay}
            />
          </Box>

          {/* Middle Section */}
          {/* *********** LED DISPLAY ************ */}
          <Box flex="0 0 40%" textAlign="center">
            <LedDisplay 
              ws={ws} 
              wsRes={wsRes}
              mode={mode} 
              hexCode={hexCode}
              strip={strip}
              syncDelay={syncDelay}
              xDimension={xDimension}
              setXDimension={setXDimension}
              yDimension={yDimension}
              setYDimension={setYDimension}
              />
          </Box>

          {/* Right Section */}
          {/* *********** ESP CLIENT LIST ************ */}
          <Box flex="0 0 30%" textAlign="center" justifyContent={"center"}>
            <EspClientList 
              ws={ws} 
              wsRes={wsRes} 
              xDimension={xDimension} 
              yDimension={yDimension}/>
          </Box>
          
        </Flex>
      </Flex>

        {/* Bottom section */}
        <Flex height="20%" align="center" pt={5}>
          <Textarea width="100%" placeholder="Enter text here" ref={textBoxRef}
          onKeyDown={(e) => {

            let key = e.key;

            // If the user has pressed enter
            if (key === 'Enter') {
              if (ws) {
                ws.send(textBoxRef.current.value) 
                ws.send("getClientState")
              }
            }
            else {
                return true;
            }
            }}
          />
        </Flex>
    </DndProvider>

        {/* <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Logo h="40vmin" pointerEvents="none" />
            <Text>
              Edit <Code fontSize="xl">src/App.js</Code> and save to reload.
            </Text>
            <Link
              color="teal.500"
              href="https://chakra-ui.com"
              fontSize="2xl"
              target="_blank"
              rel="noopener noreferrer"
            >
              Learn Chakra
            </Link>
          </VStack>
        </Grid> */}
      </Box>
    </ChakraProvider>
  );
}

export default App;
